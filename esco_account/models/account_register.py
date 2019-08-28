from odoo import models, fields, exceptions, api

class AccountPayment(models.Model):
    """To extend the fuctionality of register payment when customer invoice is paid.
    It will show and create journal entry for remaining amount."""
    _inherit = 'account.payment'

    remaining_amt_currency = fields.Many2one('res.currency', 
        string='Remaining Currency', required=True, 
        default=lambda self: self.env.user.company_id.currency_id)
    remaining_amt = fields.Monetary('Remaining Amount', 
        compute="_compute_remaining_amount")

    @api.depends('remaining_amt_currency')
    def _compute_remaining_amount(self):
        """Calculate remaining amount for the selected currency"""
        for pay in self.filtered(lambda p: p.invoice_ids):
            currency_rate = self.remaining_amt_currency.rate
            self.remaining_amt = abs(pay.payment_difference * currency_rate)
    
    def action_validate_invoice_payment(self):
        move_line=[]
        """When we validate register payment, if remaining amount returned to customer
        need to show it in invoice form."""
        if self.env.context['active_model'] == 'account.invoice' and self.remaining_amt > 0:
            active_id = self.env.context['active_id']
            if active_id:
                account_inv = self.env['account.invoice'].browse(active_id)
                account_inv.remaining_amt = self.remaining_amt
                account_inv.remaining_amt_currency = self.remaining_amt_currency.id
                """we create journal entry for remaining amount"""
                values={
                'amount': self.remaining_amt,
                'partner_id': account_inv.partner_id.id,
                'communication': self.communication,
                'payment_type': 'outbound',
                'partner_type':  self.partner_type,
                'journal_id' :  self.journal_id.id,
                'payment_date': self.payment_date,
                'currency_id' : self.remaining_amt_currency.id,
                'payment_method_id':  self.env.ref("account.account_payment_method_manual_out").id,
                }
                obj = self.sudo().create(values)
                obj.post()

        return super(AccountPayment, self).action_validate_invoice_payment()