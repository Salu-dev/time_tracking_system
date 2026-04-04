// Copyright (c) 2026, salu and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Visit", {
	refresh(frm) {
        // add button to mark updations
        frm.trigger("add_mark_updates_button");

	},
    add_mark_updates_button(frm) {

        // add check in button
        if (frm.doc.status=="Scheduled") {
            frm.add_custom_button("Check In", () => {
                frm.doc.status = "In Progress";
                get_location().then(location => {
                    frm.doc.check_in_latitude = location.latitude;
                    frm.doc.check_in_longitude = location.longitude;
                    frm.dirty();
                    frm.save();
                });
            });
            frm.add_custom_button("Cancel", () => {
                frm.doc.status = "Cancelled";
                frm.dirty();
                frm.save();
            });
       
        }
        else if (frm.doc.status=="In Progress") {
            frm.add_custom_button("Check Out", () => {
                frm.doc.status = "Completed";
                get_location().then(location => {
                    console.log(location);
                    frm.doc.check_out_latitude = location.latitude;
                    frm.doc.check_out_longitude = location.longitude;
                    frm.dirty();
                    frm.save();
                });
            });
        } 
    },
    
    
        
});

function get_location() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
               let latitude = position.coords.latitude;
               let longitude = position.coords.longitude;
               resolve({ latitude, longitude });
            }, (error) => {
                reject(error);
            });
        } else {
            reject(new Error('Geolocation is not supported by this browser.'));
        }
    });
}

