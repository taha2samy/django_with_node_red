class SensorGauge {
    constructor(elementId, details) {
        this.elementId = elementId;
        this.details = details;
        this._permissions="RC"


        this.gauge = new RadialGauge({
            renderTo: this.elementId,
            width: 200,
            height: 200,
            units: this.details.unit  || "count",
            minValue: this.details.min_value || 0,
            maxValue: this.details.max_value || 100,
            majorTicks: this.details.major_ticks || [0, 20, 40, 60, 80, 100],
            minorTicks: 5,
            highlights: this.details.high_lights || [],
            valueBox: this.details.value_box,
            valueBoxStroke: this.details.value_box || "#2C3E50",
            valueBoxBorderRadius: this.details.value_box_border_radius || 5,
            valueBoxWidth: this.details.value_box_width || 5,
            valueBoxHeight: this.details.value_box_height || 5,
            valueBoxFont: this.details.value_box_font || 'bold 16px Arial',
            valueBoxBackground: this.details.value_box_background || '#2C3E50',
            valueBoxTextColor: this.details.value_box_text_color || '#fff',
        }).draw();
    }
    

    setValue(value) {
        this.gauge.value = value;
        document.getElementById(this.elementId + "-value").textContent = value;
    }

    setStatus(status) {
        const statusElement = document.getElementById(this.elementId + "-status");
        if (status === 'connected' | status == "1") {
            statusElement.className = 'status-indicator status-active';
        } else if (status === 'disconnected' | status == "0") {
            statusElement.className = 'status-indicator status-inactive';
        } else {
            statusElement.className = 'status-indicator';
        }

    }

    get permissions() {
        return this._permissions;
    }

    // Setter for permissions
    set permissions(value) {
        this._permissions = value;

        
        

        // Perform additional logic here if needed
    }


}
