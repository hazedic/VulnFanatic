from binaryninja import *
from ..trackers.function_tracer2 import FunctionTracer

class Highlighter2(BackgroundTaskThread):
    def __init__(self,bv,call_instruction,current_function,highlight):
        BackgroundTaskThread.__init__(self, "[VulnFanatic] Testing tracing ... ", True)
        self.call_instruction = call_instruction
        self.bv = bv
        self.current_function = current_function
        self.high = highlight

    def append_comment(self,addr,text):
        current_comment = self.bv.get_comment_at(addr)
        if text in current_comment:
            return
        if not "[VulnFanatic]" in current_comment:
            current_comment = "[VulnFanatic]\n" + text
            self.bv.set_comment_at(addr,current_comment)
            return
        self.bv.set_comment_at(addr,current_comment + "\n" + text)
    
    def run(self):
        if self.high:
            self.highlight()
        else:
            self.clear()

    def clear(self):
        #TODO
        fun_trace = FunctionTracer(self.bv)
        results = fun_trace.selected_function_tracer(self.call_instruction,self.current_function)
        self.progress = "[VulnFanatic] Completed tracing. Clearing highlights ..."
        for src in results["sources"]:
            # Highlight source if any
            if src["def_instruction_address"] != None:
                self.bv.set_comment_at(src["def_instruction_address"],"")
                src["function"].source_function.set_user_instr_highlight(src["def_instruction_address"],binaryninja.enums.HighlightStandardColor.NoHighlightColor)
            if "param" in src["var_type"]:
                # Parameter
                # THIS IS WORKAROUND ONLY UNTIL FUNCTION COMMENTS START WORKING
                self.bv.set_comment_at(list(src["function"].instructions)[src["source_basic_block_start"]].address,"")
            # Highlight call stack
            for call in src["call_stack"]:
                if type(call["function"]) == binaryninja.Function:
                    call["function"].set_user_instr_highlight(call["address"],binaryninja.enums.HighlightStandardColor.NoHighlightColor)
                else:
                    call["function"].source_function.set_user_instr_highlight(call["address"],binaryninja.enums.HighlightStandardColor.NoHighlightColor)
            # Highlight function calls
            for fun_call in src["function_calls"]:
                self.bv.set_comment_at(fun_call["call_address"],"")
                fun_call["at_function"].set_user_instr_highlight(fun_call["call_address"],binaryninja.enums.HighlightStandardColor.NoHighlightColor)


    def highlight(self):
        fun_trace = FunctionTracer(self.bv)
        results = fun_trace.selected_function_tracer(self.call_instruction,self.current_function)
        self.progress = "[VulnFanatic] Completed tracing. Highlighting important points ..."
        for src in results["sources"]:
            # Highlight source if any
            if src["def_instruction_address"] != None:
                self.append_comment(src["def_instruction_address"],f"Source of parameter[{src['param']}]({src['param_var']})")
                src["function"].source_function.set_user_instr_highlight(src["def_instruction_address"],binaryninja.enums.HighlightStandardColor.RedHighlightColor)
            if "param" in src["var_type"]:
                # Parameter
                # THIS IS WORKAROUND ONLY UNTIL FUNCTION COMMENTS START WORKING
                self.append_comment(list(src["function"].instructions)[src["source_basic_block_start"]].address,f"Parameter {str(src['var'])} source of parameter[{src['param']}]({src['param_var']})")
            # Highlight call stack
            for call in src["call_stack"]:
                if type(call["function"]) == binaryninja.Function:
                    call["function"].set_user_instr_highlight(call["address"],binaryninja.enums.HighlightStandardColor.GreenHighlightColor)
                else:
                    call["function"].source_function.set_user_instr_highlight(call["address"],binaryninja.enums.HighlightStandardColor.GreenHighlightColor)
            # Highlight function calls
            for fun_call in src["function_calls"]:
                # Avoid overpainting green stuff:
                if fun_call["at_function"].get_instr_highlight(fun_call["call_address"]).color == 0:
                    fun_call["at_function"].set_user_instr_highlight(fun_call["call_address"],binaryninja.enums.HighlightStandardColor.RedHighlightColor)
                self.append_comment(fun_call["call_address"],f"Affecting parameter[{src['param']}]({src['param_var']})")
                



   