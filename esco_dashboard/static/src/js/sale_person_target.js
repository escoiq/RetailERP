odoo.define('sales_person_target.sale_person_target', function (require) {
"use strict";

var core = require('web.core');
var KanbanRecord = require('web.KanbanRecord');
//var Model = require('web.Model');
var _t = core._t;
console.log("Callled-----------------",KanbanRecord);
KanbanRecord.include({
    events: _.defaults({
        'click .sales_person_target_definition': 'on_sales_person_target_click',
    }, KanbanRecord.prototype.events),

    on_sales_person_target_click: function(ev) {
        ev.preventDefault();

        this.$target_input = $('<input>');
        this.$('.o_kanban_primary_bottom').html(this.$target_input);
        this.$('.o_kanban_primary_bottom').prepend(_t("Set an invoicing target: "));
        this.$target_input.focus();

        var self = this;
        /* this.$target_input.blur(function() {
            var value = Number(self.$target_input.val());
            if (isNaN(value)) {
                self.do_warn(_t("Wrong value entered!"), _t("Only Integer Value should be valid."));
            } else {
                new Model('sales.person.target').call('write', [[self.id], { 'target_amount': value }]).done(function() {
                    self.trigger_up('kanban_record_update', {id: self.id});
                });
            }
        }); */
    },
});

});
