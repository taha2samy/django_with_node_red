class SensorChart {
    constructor(elementId, details) {
        this.elementId = elementId;
        this.details = details;
        this._permissions="RC"

        // إعداد الرسم البياني باستخدام Chart.js
        const ctx = document.getElementById(this.elementId).getContext('2d');
        this.chart = new Chart(ctx, {
            type: details.type||'line', 
            data: {
                labels: Array.from({ length: 10 }, (_, i) => i + 1), 
                datasets: [{
                    label: this.details.title || 'Sensor Data',
                    data: Array(this.details.max_point||10).fill(0),
                    
                    
                    borderColor: this.details.border_color ||'rgba(0, 123, 255, 1)',
                    backgroundColor:this.details.background_color||'rgba(0, 123, 255, 0.2)',
                    borderWidth: this.border_width || 2,
                    fill: this.details.fill == 1 ? true : false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    setValue(values) {
        if (Array.isArray(values)) {
            if (values.length === 2) {
                // إذا كانت القائمة تحتوي على عنصرين: x, y
                const [x, y] = values;
                this.chart.data.labels.push(x); // تحديث محور x
                this.chart.data.labels.shift(); // إزالة أقدم قيمة في محور x
                this.chart.data.datasets[0].data.push(y); // تحديث محور y
                this.chart.data.datasets[0].data.shift(); // إزالة أقدم قيمة في محور y
                document.getElementById(this.elementId + "-value").textContent = y; // تحديث القيمة المعروضة
            } else if (values.length === 1) {
                // إذا كانت القائمة تحتوي على عنصر واحد: y فقط
                const y = values[0];
                const nextX = this.chart.data.labels.length + 1; // توليد قيمة تلقائية لمحور x
                this.chart.data.labels.push(nextX); // تحديث محور x
                this.chart.data.labels.shift(); // إزالة أقدم قيمة في محور x
                this.chart.data.datasets[0].data.push(y); // تحديث محور y
                this.chart.data.datasets[0].data.shift(); // إزالة أقدم قيمة في محور y
                document.getElementById(this.elementId + "-value").textContent = y; // تحديث القيمة المعروضة
            } else {

            }
        } else {
            
            const nextX = this.chart.data.labels.length + 1; // توليد قيمة تلقائية لمحور x
            this.chart.data.labels.push(nextX); // تحديث محور x
            this.chart.data.labels.shift(); // إزالة أقدم قيمة في محور x
            this.chart.data.datasets[0].data.push(values); // تحديث محور y
            this.chart.data.datasets[0].data.shift(); // إزالة أقدم قيمة في محور y
            document.getElementById(this.elementId + "-value").textContent = values; // تحديث القيمة المعروضة

        }
        this.chart.update();
    }


    setStatus(status) {
        const statusElement = document.getElementById(this.elementId + "-status");
        if (status === 'connected' || status == "1") {
            statusElement.className = 'status-indicator status-active';
        } else if (status === 'disconnected' || status == "0") {
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
    