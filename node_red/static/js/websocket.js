const socketUrl = `ws://${window.location.host}/browser/simple/`;
const socket = new WebSocket(socketUrl);
socket.onopen = function(event) {
    console.log('WebSocket is open now.');
};

socket.onmessage = function(event) {
   
    const data = JSON.parse(event.data);
    console.log(data)
    if (data.type === 'check_connection_element' && data.element_id && data.status) {
        const elementList = window.all_elements[data.element_id];
        if (elementList) {
            elementList.forEach(element => {
                element.setStatus(data.status == "connected" ? 1 : 0)
            });
        } else {
            console.log(`No elements found for element_id: ${data.element_id}`);
        }
    }


    if (data.type === 'message_element' && data.element_id) {
        const elementList = window.all_elements[data.element_id];
        if (elementList) {
            elementList.forEach(element => {
                element.setValue(data.message.value)
            });
        } else {
            console.log(`No elements found for element_id: ${data.element_id}`);
        }
    } else {
    }
    if (data.type === 'subscribe' && data.element_id && data.subscribed== true) {
        console.log(data)
        const elementList = window.all_elements[data.element_id];
        if (elementList) {
            elementList.forEach(element => {
                element.setStatus(data.connected)
                element.permissions=data.permissions
            });
        } else {
            console.log(`No elements found for element_id: ${data.element_id}`);
        }
    } else {
    }
    
    
};

socket.onclose = function(event) {
    console.log('WebSocket is closed now.');
};

socket.onerror = function(error) {
    console.error('WebSocket error observed:', error);
};

// Example function to send a message
function sendMessage(message) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(message);
    } else {
        console.error('WebSocket is not open. Ready state:', socket.readyState);
    }
}

(function() {
    if (typeof window.all_elements === 'undefined') {
    window.all_elements = {};
    }

})();
socket.onopen = function(event) {
    for (const key in window.all_elements) {
        const message = JSON.stringify({ type: 'subscribe', element_id: key });
        sendMessage(message);

    }
    
};


