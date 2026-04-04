frappe.listview_settings['Customer'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Schedule Visit'), function() {
            let selected_customers = listview.get_checked_items();
            console.log(selected_customers);
            if(selected_customers.length === 0){
                frappe.msgprint(__('Please select at least one Customer'));
                return; 
            }

            let customer_names = selected_customers.map(c => c.name);
            console.log("Customer names:", customer_names);
            frappe.prompt([
                {
                    fieldname: 'selected_date',
                    fieldtype: 'Date',
                    label: 'Select Date',
                    reqd: 1
                }
            ],
            function(values){
                console.log("Calling API with customers:", customer_names);
                console.log("Scheduled date:", values.selected_date);
                frappe.call({
                    method: "time_tracking_system.api.schedule_visit",
                    args: {
                        customers: JSON.stringify(customer_names),
                        scheduled_date: values.selected_date
                    },
                    callback: function(r) {
                        if(r.message){
                            frappe.msgprint(__('Processed: ') + r.message);
                        }
                    }
                });
            },
            __('Select Date'),
            __('Submit')
            );
        });
    }
};