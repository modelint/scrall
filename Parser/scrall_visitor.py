""" scrall_visitor.py """
from arpeggio import PTNodeVisitor

class ScrallVisitor(PTNodeVisitor):

    def visit_space(self, node, children):
        """Discard spaces"""
        return None

    def visit_name(self, node, children):
        """Words and delmiters joined to form a complete name"""
        name = ''.join(children)
        return name

    def visit_signal(self, node, children):
        """Send a signal to an instance"""
        return {'event': children[0], 'instance': children[1]}

    def visit_addition(self, node, children):
        return children


    def visit_term(self, node, children):
        return children

    def visit_scalar_expr(self, node, children):
        return children

    def visit_assign_scalar(self, node, children):
        return children

    def visit_activity(self, node, children):
        return children