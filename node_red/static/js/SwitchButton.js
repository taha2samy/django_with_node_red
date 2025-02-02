class SwitchButton {
    constructor(elementId,details,real_element_id) {
        this.elementId = elementId;
        this.real_element_id=real_element_id
        this.details=details
        // Get the toggle button element
        this.statusElement = document.getElementById(this.elementId + '-status');
        this.valueElement = document.getElementById(this.elementId+"-input")
        this.labelElement = document.getElementById(this.elementId+"-label")
        this._permissions="RC"
        // Initialize the switch button with 'off' state
        this.valueElement.addEventListener("change", this.action.bind(this))


    }
    action(event)
    {
        if (socket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket is not open. ReadyState: ' + socket.readyState);
            return;
        }
        const message = JSON.stringify({
            type: 'message_element',
            element_id: this.real_element_id,
            message: { value: this.valueElement.checked ? 1 : 0 }
        });
        socket.send(message);

        socket.onerror = function(error) {
            console.error('WebSocket error observed:', error);
        };
    }
    



    setStatus(status) {
        // Change status indicator class based on state
        if (status === 'connected' || status == "1") {
            this.statusElement.className = 'status-indicator status-active';
        } else if (status === 'disconnected' || status == "0") {
            this.statusElement.className = 'status-indicator status-inactive';
        } else {
            this.statusElement.className = 'status-indicator';
        }    }

    setValue(value) {
        // Update the value displayed in the card
        this.valueElement.value = (value == 'on' )? 'On' : 'Off';
        this.valueElement.checked=(value == 1 )? true : false
        this.labelElement.innerHTML = (value == 1) ? (this.details.text_on || "On") : (this.details.text_off || "Off");
    }
    get permissions() {
        return this._permissions;
    }

    // Setter for permissions
    set permissions(value) {
        this._permissions = value;
        if (this._permissions === "RC")
            {
                this.valueElement.disabled = false


            }else{

                this.valueElement.disabled = true

            }
        
        

        // Perform additional logic here if needed
    }
}
