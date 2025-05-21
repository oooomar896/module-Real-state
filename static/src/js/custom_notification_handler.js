odoo.define('estate_molhimah.CustomNotificationHandler', function (require) {
    "use strict";

    const { registry } = require("@web/core/registry");
    const { bus } = require("@web/core/bus/bus_service"); // Correct way to get bus in Odoo 16+
    const { notificationService } = require("@web/core/notifications/notification_service"); // For displaying notifications

    // It's often better to start services or listeners when the web client starts.
    // For Odoo 16+, services are typically used.
    // A simple way to listen to bus events without creating a full new service:
    // Ensure this code runs after the bus_service is available.

    // We need to get the bus instance from the environment if possible, or use the global bus.
    // The notification service also needs to be properly invoked.
    // A more robust way in Odoo 16+ is to interact with services through the component env
    // or by defining a new service that has dependencies on bus_service and notification_service.

    // Let's try a simpler approach that should work for straightforward bus listening.
    // Get the main bus instance (this might need to be adapted based on exact Odoo version's JS environment setup)
    // The global bus `core.bus` from older versions is not the direct way anymore.
    // We should use the bus service from the registry or environment.

    // This approach might be too simplistic for Odoo 16+ as services are preferred.
    // A better way for Odoo 16+ would be to define a service that listens to the bus.
    // However, to keep it concise for now, let's attempt a direct listener setup.
    // This part needs to be carefully tested as direct bus listening setup outside services/components has changed.

    // A more standard way to add such a listener is to do it from within a component, 
    // or create a new service. Let's try to use a simpler startup hook if possible for now.

    // Odoo 16+ uses a different way to access services. Let's make this a service.

    const customNotificationListener = {
        dependencies: ["bus_service", "notification"],
        start(env, { bus_service, notification }) {
            bus_service.subscribe("estate_molhimah_notification", (payload) => {
                if (payload) {
                    notification.add(payload.message, {
                        title: payload.title,
                        type: payload.type || 'info', // Default to info if type not provided
                        sticky: payload.sticky || false,
                        className: payload.className || ''
                    });
                }
            });
            // You can also use addChannel for specific channel-based communication if needed
            // bus_service.addChannel("estate_molhimah_notification_channel");
            // bus_service.subscribe("estate_molhimah_notification_channel", ... );
        },
    };

    registry.category("services").add("customNotificationListener", customNotificationListener);

    // Return something if it were a classical module, but for services, adding to registry is key.
    return customNotificationListener; 
}); 