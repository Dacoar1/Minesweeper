#!/usr/bin/env python3
from csp_templates import Constraint, BooleanCSP
from typing import List, Optional


class Solver:
    """
    Class for solving BooleanCSP.

    Main methods:
    - forward_check
    - solve
    - infer_var
    """

    def __init__(self):
        # Your implementation goes here.
        
        pass

    def forward_check(self, csp: BooleanCSP) -> Optional[List[int]]:
        """
        Perform forward checking on any unchecked constraints in the given CSP.
        Return a list of variables (if any) whose values were inferred.
        If a contradiction is found, return None.
        """
        # Your implementation goes here.
        
        inferred_variables = []
        true_vars = []
        while csp.unchecked:
            constraint = csp.unchecked.popleft()
            unknown_vars = [var for var in constraint.vars if csp.value[var] is None] 
            true_vars=[var for var in constraint.vars if csp.value[var] is True]
            
            if len(true_vars)+len(unknown_vars) == constraint.count:
                for var in unknown_vars:
                    csp.set(var, True)
                    inferred_variables.append(var)     
                       
            elif constraint.count == len(true_vars):
                for var in unknown_vars:
                    csp.set(var, False)
                    inferred_variables.append(var)
                    
       
            elif (len(true_vars) > constraint.count or len(true_vars) + len(unknown_vars) < constraint.count):
                csp.reset()
                return None
        
        return inferred_variables
            

    def solve(self, csp: BooleanCSP) -> Optional[List[int]]:
        """
        Find a solution to the given CSP using backtracking.
        The solution will not include values for variables
        that do not belong to any constraints.
        Return a list of variables whose values were inferred.
        If no solution is found, return None.
        """
        vars = [var for var in range(csp.num_vars) if csp.var_constraints[var]] #list of variables that belong to constraints
        
        def backtrack(csp, inferred_variables):
            if len(inferred_variables) == len(vars): #we check if all variables have been assigned
                return inferred_variables

            var = select_unassigned_variable(csp,inferred_variables) #we select the next variable to assign
            for value in [True,False]: #we select the next value to assign
                csp.set(var, value)
                if is_consistent(var, csp):
                    inferred_variables[var] = value
                    if self.forward_check(csp) is not None:
                        inferred_variables.update(self.forward_check(csp))
                        
                    result = backtrack(csp,inferred_variables)
                    if result is not None:
                        return result
                    del inferred_variables[var]
                csp.set(var, None)
            return None

        def select_unassigned_variable(csp, inferred_variables):  #we select the variable that appears in the most constraints
            unassigned_vars = [var for var in vars if var not in inferred_variables]
            return max(unassigned_vars, key=lambda var: len(csp.var_constraints[var]))

        def is_consistent(var,csp): #check if the current assigment is consistent with the constraints
            for constraint in csp.constraints:
                if len([var for var in constraint.vars if csp.value[var] is True]) > constraint.count or len([var for var in constraint.vars if csp.value[var] is True]) + len([var for var in constraint.vars if csp.value[var] is None]) < constraint.count:
                    return False
            return True
        
        inferred_variables = {}
        result=backtrack(csp,inferred_variables)  
        return result 
                        
            
            

    def infer_var(self, csp: BooleanCSP) -> int:
        """
        Infer a value for a single variable if possible using a proof by contradiction.
        If any variable is inferred, return its index; otherwise return -1.
        """
        vars = [var for var in range(csp.num_vars) if csp.var_constraints[var]]
        #variables that have been tried(its value has been set to True or False)
        infered_vars = [var for var in vars if csp.value[var] is not None]
        tried_vars = []
        untried_vars = [var for var in vars if var not in infered_vars]
        while untried_vars:
            
            var=min(untried_vars, key=lambda var: len(csp.var_constraints[var]))
            
            tried_vars.append(var)
            untried_vars.remove(var)
            if csp.value[var] is not None:
                continue  # Skip already assigned variables
            
            # Temporarily assign True and False to the variable and check for contradictions
            for val in [True, False]:
                csp.set(var, val)
                
                if not self.solve(csp):
                    # If a contradiction is found, the opposite value must be true
                    infered_vars.append(var)
                    csp.set(var, not val)
                    return var
                
                for var,val in enumerate(csp.value):
                    if var not in infered_vars:
                        csp.set(var, None)
                 
        return -1
