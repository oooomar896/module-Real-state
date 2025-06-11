odoo.define('estate_molhimah.ContractFormLiveUpdate', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const { useEffect, useRef, useState } = owl;
    const { useService } = require("@web/core/utils/hooks");
    const core = require('web.core');

    // We need to patch the FormController to make it aware of our live updates.
    // This is a common pattern in Odoo for extending existing views/controllers.

    // It's generally safer to patch specific methods or behaviors rather than overriding entire classes,
    // but for listening to bus events and reacting, patching the setup or onMounted is common.

    // For Odoo 16+, direct patching of FormController might be less straightforward due to an evolving JS framework.
    // A more robust approach might involve creating a custom form view and controller if simple patching isn't enough,
    // or using a service that interacts with the form view if possible.

    // Let's attempt a patch that focuses on listening to the bus service when the component is mounted.

    const ContractFormLiveUpdate = (OriginalFormController) => class extends OriginalFormController {
        setup() {
            super.setup();
            this.busService = useService("bus_service");
            const channel = "real_estate_contract_state_update_channel";

            useEffect(() => {
                const onNotification = (payload) => {
                    if (!payload || !this.model || !this.model.root) return;

                    const currentRecordId = this.model.root.resId;
                    const updatedContractId = payload.contract_id;
                    const newState = payload.new_state;

                    // Check if the update is for the currently viewed contract and the model is 'real.estate.contract'
                    if (this.model.root.resModel === 'real.estate.contract' && currentRecordId === updatedContractId) {
                        // The model's `update` method can be used to change field values
                        // and trigger a re-render. This is a complex area as it depends on how the FormRenderer
                        // and its underlying components react to data changes.
                        
                        // We need to update the record in a way that the UI reflects it.
                        // This might involve specifically telling the model to save/reload the record or parts of it.
                        // The simplest way to reflect a change is often to reload the record, 
                        // but that can be disruptive if the user is editing.

                        // A less disruptive way is to update the specific field in the model's data
                        // and ensure the renderer picks it up. 
                        // Odoo's model has ways to update data and notify components.

                        // Let's try to update the value in the model and then trigger a re-render of the statusbar field specifically if possible,
                        // or a more general update if needed.
                        // The `this.model.notify` or similar methods might be relevant, or `this.model.load` to refresh.
                        
                        // For a field like 'state' used in a statusbar, we'd want the statusbar to re-render.
                        // The core of Odoo's form view handles rendering based on record data.
                        // So, updating the record data for the 'state' field should be the primary goal.

                        // `this.model.root.update` can be used to set a new value for a field.
                        // It should then trigger the necessary re-renders.
                        this.model.root.update({ 'state': newState }).then(() => {
                            // Potentially, we might need to explicitly tell parts of the view to re-render
                            // or ensure that the change detection picks this up correctly.
                            // For many standard widgets like statusbar, updating the record data via model.root.update
                            // should be sufficient if the field is part of the viewDef.
                            console.log(`Contract ${updatedContractId} state updated to ${newState} in UI.`);
                            // If the view doesn't refresh automatically (e.g. statusbar color/text), a more forceful reload might be needed.
                            // this.model.reload(this.model.root.id);
                            // However, reload can be disruptive if user is editing other fields.
                            // A targeted update is preferred.
                        }).catch(error => {
                            console.error("Error updating contract state in UI:", error);
                        });
                    }
                };

                this.busService.subscribe(channel, onNotification);
                // Cleanup on unmount
                return () => this.busService.unsubscribe(channel, onNotification);
            }, () => []); // Empty dependency array means this effect runs once on mount and cleanup on unmount
        }
    };

    // Patching the FormController
    // This requires that the FormController is available in the require('web.FormController') path.
    // In Odoo 16, the view system is more component-based (Owl).
    // The way to extend/patch controllers might differ slightly or require different techniques
    // compared to older versions.
    
    // A more modern way for Odoo 16+ might involve creating a custom hook or component extension.
    // However, patching is still a mechanism used. We need to ensure this patch is applied correctly.
    // It might be better to patch `FormRenderer` or a specific widget if the goal is just to update its display.
    // But since `state` affects the statusbar which is part of the FormController's general responsibility,
    // patching the controller to update its model makes sense.

    // The registry for views might be the place to extend specific controllers for a model.
    // For example, view_registry.get('form').Controller.extend({...})
    // However, `FormController.registry.add` or `patch` is more common in newer Odoo versions for Owl components.

    // Let's use a more standard Odoo 16+ way of patching Owl components if FormController is an Owl component.
    // If FormController is still a legacy class, `extend` would be used.
    // Assuming FormController or its equivalent in Odoo 16+ can be patched this way:
    
    // This specific way of patching might need adjustment based on Odoo's exact version (16, 17, etc.)
    // For Odoo 16+, `patch` from `@web/core/utils/patch` is often used.
    // Let's assume for now that `FormController` can be extended or patched.
    // We need to ensure this JS is loaded and the patch is applied.

    // A more robust way: Get the form controller from the registry and patch it.
    const { formView } = require('@web/views/form/form_view');
    const { patch } = require('@web/core/utils/patch');

    patch(formView.Controller.prototype, 'estate_molhimah.ContractFormLiveUpdate', {
        setup() {
            this._super.apply(this, arguments); // Call original setup
            this.busService = useService("bus_service");
            const channel = "real_estate_contract_state_update_channel";
            
            // Using Owl's useEffect for lifecycle management
            useEffect(() => {
                const onNotification = (payload) => {
                    if (!payload || !this.model || !this.model.root) {
                        console.warn("Live update: No payload or model not ready.");
                        return;
                    }

                    const currentRecordId = this.model.root.resId;
                    const updatedContractId = payload.contract_id;
                    const newState = payload.new_state;
                    
                    // Log for debugging
                    // console.log(`Live update: Received for contract ${updatedContractId}, current is ${currentRecordId}, model is ${this.model.root.resModel}`);

                    if (this.model.root.resModel === 'real.estate.contract' && currentRecordId === updatedContractId) {
                        console.log(`Live update: Attempting to update contract ${updatedContractId} to state ${newState}.`);
                        
                        // Use the official way to update record data, which should trigger re-render
                        this.model.root.update({ 'state': newState })
                            .then(() => {
                                // This should ideally re-render the parts of the form that depend on 'state'.
                                // The statusbar widget should react to this change.
                                // If it doesn't, further investigation into how the statusbar specifically re-renders would be needed.
                                // Sometimes a forced re-render of a component or the whole view might be attempted, but it's a last resort.
                                // For example: this.render(); // if available and appropriate.
                                console.log(`Contract ${updatedContractId} UI state update to ${newState} initiated.`);
                            })
                            .catch(error => {
                                console.error("Error updating contract state in UI via model.root.update:", error);
                            });
                    } else {
                        // console.log("Live update: Not for current record or model.");
                    }
                };

                this.busService.subscribe(channel, onNotification);
                return () => {
                    this.busService.unsubscribe(channel, onNotification);
                    // console.log("Live update: Unsubscribed from contract state updates.");
                };
            }, () => [this.model.root.resId]); // Re-run effect if record ID changes (e.g. navigating between records)
        }
    });

    // This doesn't return anything as it's a patch.
    // The patch utility modifies the FormController prototype directly.
}); 