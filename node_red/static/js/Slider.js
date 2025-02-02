class SliderButton {
    constructor(elementId, details, real_element_id) {
        this.elementId = elementId;
        this.real_element_id = real_element_id;
        this.details=details
        // Get the slider element
        this.sliderElement = document.getElementById(this.elementId + '-input');
        this.statusElement = document.getElementById(this.elementId + '-status');
        this.labelElement = document.getElementById(this.elementId + '-label');
        this._permissions = "RC";

        // Initialize the slider value
        this.sliderElement.addEventListener("input", this.action.bind(this));
    }

    action(event) {
        if (socket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket is not open. ReadyState: ' + socket.readyState);
            return;
        }
        const message = JSON.stringify({
            type: 'message_element',
            element_id: this.real_element_id,
            message: { value: this.sliderElement.value }
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
        }
    }

    setValue(value) {
        // Update the slider value
        this.sliderElement.value = value;
        this.labelElement.innerText=value+(this.details.unit||"")
    }

    get permissions() {
        return this._permissions;
    }

    set permissions(value) {
        this._permissions = value;
        if (this._permissions === "RC") {
            this.sliderElement.disabled = false;
        } else {
            this.sliderElement.disabled = true;
        }
    }
}