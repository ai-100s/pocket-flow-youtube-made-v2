class Node:
    def __init__(self, max_retries=1, wait=0):
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0
        self._transitions = {}
        self.params = {}

    def prep(self, shared):
        return None

    def exec(self, prep_res):
        raise NotImplementedError

    def post(self, shared, prep_res, exec_res):
        return "default"

    def exec_fallback(self, prep_res, exc):
        raise exc

    def run(self, shared_store):
        # Simplified run logic for placeholder
        prep_result = self.prep(shared_store)
        try:
            exec_result = self.exec(prep_result)
        except Exception as e:
            # Simplified retry/fallback, real PocketFlow is more complex
            # print(f"Node {self.__class__.__name__} exec error: {e}")
            exec_result = self.exec_fallback(prep_result, e)
        
        action = self.post(shared_store, prep_result, exec_result)
        return action if action is not None else "default"

    def __rshift__(self, other_node):
        self._transitions["default"] = other_node
        return other_node # Allow chaining

    def __sub__(self, action_name):
        # Placeholder for named transitions, e.g. node - "action" >> next_node
        # This would typically return an intermediate object to handle the >> part
        # For simplicity, we'll just store it directly for now if used in a specific way
        class ActionLinker:
            def __init__(self, node, action):
                self.node = node
                self.action = action
            def __rshift__(self, next_node):
                self.node._transitions[self.action] = next_node
                return next_node
        return ActionLinker(self, action_name)

    def set_params(self, params_dict):
        self.params.update(params_dict)

class BatchNode(Node):
    def exec(self, item): # exec for BatchNode processes one item
        raise NotImplementedError

    # Actual batch execution would be handled by the Flow or a specialized run method
    # For this placeholder, the Flow will need to iterate if it encounters a BatchNode
    # Or, we can adjust the 'run' method slightly if a batch node is run directly (less ideal)
    def run(self, shared_store):
        # Simplified run for BatchNode
        iterable_prep_res = self.prep(shared_store)
        exec_results_list = []
        if iterable_prep_res is None:
            iterable_prep_res = []
            
        for item in iterable_prep_res:
            try:
                # In a real BatchNode, exec would be called per item by the framework
                exec_result_item = super().exec(item) # Call the single-item exec
            except Exception as e:
                # print(f"BatchNode {self.__class__.__name__} exec error for item {item}: {e}")
                exec_result_item = self.exec_fallback(item, e)
            exec_results_list.append(exec_result_item)
        
        # prep_res for post in BatchNode is the original iterable output of prep()
        action = self.post(shared_store, iterable_prep_res, exec_results_list)
        return action if action is not None else "default"

class Flow(Node): # A Flow can also be a Node for nesting
    def __init__(self, start_node, max_retries=1, wait=0):
        super().__init__(max_retries, wait)
        self.start_node = start_node
        self.current_node = None

    def run(self, shared_store):
        # This is a very simplified run method for a Flow
        print(f"--- Running Flow: {self.__class__.__name__} ---")
        self.current_node = self.start_node
        final_action = "default" # Default action if the flow completes

        # Flow-level prep (if any)
        flow_prep_res = super().prep(shared_store)

        loop_count = 0 # Safety break for loops
        max_loops = 20 

        while self.current_node and loop_count < max_loops:
            print(f"  Flow: Executing node {self.current_node.__class__.__name__} with params {self.current_node.params}")
            
            # Merge flow params into current node params (simplified)
            # In real PocketFlow, param inheritance is more structured
            merged_params = self.params.copy()
            merged_params.update(self.current_node.params)
            self.current_node.set_params(merged_params)

            # Special handling for BatchNode within a Flow
            if isinstance(self.current_node, BatchFlow):
                # BatchFlow.run() itself will handle iterating its sub-flow
                action = self.current_node.run(shared_store) # BatchFlow has its own run
            elif isinstance(self.current_node, BatchNode):
                # This is a simplified way a Flow might run a BatchNode
                # A real framework would abstract this better
                iterable_prep_res = self.current_node.prep(shared_store)
                exec_results_list = []
                if iterable_prep_res is None: iterable_prep_res = []
                
                item_params_base = self.current_node.params.copy()

                for idx, item_data in enumerate(iterable_prep_res):
                    # For BatchNode, item_data might be the data itself or a dict containing params
                    # Based on design.md's ProcessTopic, it seems `prep` returns a list of topics (data items).
                    # The params for each `exec` call on a BatchNode item are typically derived or passed.
                    # Here, we assume `exec` on BatchNode takes the item directly.
                    # If item-specific params were needed for exec, prep would return list of dicts.
                    
                    # print(f"    BatchNode item {idx}: {item_data}")
                    try:
                        # exec method of BatchNode is defined to take a single item
                        exec_result_item = self.current_node.exec(item_data) 
                    except Exception as e:
                        exec_result_item = self.current_node.exec_fallback(item_data, e)
                    exec_results_list.append(exec_result_item)
                
                action = self.current_node.post(shared_store, iterable_prep_res, exec_results_list)

            else: # Regular Node or nested Flow (which is also a Node)
                action = self.current_node.run(shared_store)
            
            final_action = action # Store last action
            self.current_node = self.current_node._transitions.get(action)
            if not self.current_node:
                print(f"  Flow: Action \'{action}\' leads to no next node. Flow ends.")
            loop_count +=1
        if loop_count >= max_loops:
            print(f"  Flow: Reached max loop count ({max_loops}). Terminating flow to prevent infinite loop.")
        
        # Flow-level post (if any)
        # exec_res for a Flow's post method is typically None or a collected result, passing None for simplicity
        flow_final_action = super().post(shared_store, flow_prep_res, None) 
        print(f"--- Flow {self.__class__.__name__} finished ---")
        return flow_final_action if flow_final_action != "default" else final_action

# BatchFlow is a Flow that runs its sub-flow multiple times based on items from its own prep
class BatchFlow(Flow):
    def run(self, shared_store):
        print(f"--- Running BatchFlow: {self.__class__.__name__} ---")
        # BatchFlow's prep returns a list of parameter sets for its sub-flow
        param_sets = self.prep(shared_store)
        if param_sets is None: param_sets = []
        
        batch_flow_results = [] # To store results from each sub-flow run

        for i, params_for_subflow_run in enumerate(param_sets):
            print(f"  BatchFlow: Iteration {i+1}/{len(param_sets)} with params {params_for_subflow_run}")
            
            # Create a temporary shared store or manage state carefully if sub-flow runs modify it heavily
            # For simplicity, we use the same shared_store, but this can have side effects
            # A more robust BatchFlow might isolate shared_store changes per iteration or manage it.

            # Set params for the sub-flow (self.start_node is the sub-flow)
            # Important: The sub-flow (self.start_node) itself is a Flow instance.
            # We need to ensure it has its own params distinct from BatchFlow's params if needed.
            # The design.md suggests ProcessTopic is a BatchNode, and contentBatch is a (conceptual) subgraph.
            # Let's assume the `start_node` of BatchFlow is the flow to be run for each item.

            # Store original params of the sub-flow (which is self.start_node)
            original_sub_flow_params = self.start_node.params.copy()
            
            # Merge BatchFlow's main params with the item-specific params
            current_run_params = self.params.copy()
            current_run_params.update(params_for_subflow_run) # item_params overwrite flow_params
            self.start_node.set_params(current_run_params)
            
            sub_flow_result_action = self.start_node.run(shared_store) # Run the sub-flow
            batch_flow_results.append({
                "params": current_run_params,
                "result_action": sub_flow_result_action,
                # "shared_state_snapshot": shared_store.copy() # Optional: if you need to capture state
            })

            # Restore original params to the sub-flow for the next iteration or subsequent uses
            self.start_node.set_params(original_sub_flow_params)

        # BatchFlow's post processes all results from the sub-flow runs
        # prep_res for BatchFlow's post is the list of param_sets
        final_action = self.post(shared_store, param_sets, batch_flow_results) 
        print(f"--- BatchFlow {self.__class__.__name__} finished ---")
        return final_action if final_action is not None else "default" 