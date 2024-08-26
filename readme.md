---

### Node-RED Configuration

The following Node-RED flow is designed to work when Node-RED is running on port `1881` on a local server. If the server's URL changes, make sure to update the external URL in `consumer.py` to reflect the new configuration.

#### Node-RED Flow

```json
[
    {
        "id": "a7034deaa5ae9aea",
        "type": "websocket out",
        "z": "c2d71647e91e29d4",
        "name": "",
        "server": "51845eb271625baa",
        "client": "",
        "x": 820,
        "y": 220,
        "wires": []
    },
    {
        "id": "9a1b51147bbdbd94",
        "type": "websocket in",
        "z": "c2d71647e91e29d4",
        "name": "",
        "server": "51845eb271625baa",
        "client": "",
        "x": 190,
        "y": 220,
        "wires": [
            [
                "5594dc667bf68351"
            ]
        ]
    },
    {
        "id": "7462ed6aed72ad5b",
        "type": "switch",
        "z": "c2d71647e91e29d4",
        "name": "",
        "property": "group_id",
        "propertyType": "msg",
        "rules": [
            {
                "t": "eq",
                "v": "Slider",
                "vt": "str"
            }
        ],
        "checkall": "true",
        "repair": false,
        "outputs": 1,
        "x": 290,
        "y": 320,
        "wires": [
            [
                "f076b95364de7cd4"
            ]
        ]
    },
    {
        "id": "f076b95364de7cd4",
        "type": "ui_slider",
        "z": "c2d71647e91e29d4",
        "name": "slider",
        "label": "slider",
        "tooltip": "eng",
        "group": "f1fba85d.a4d008",
        "order": 0,
        "width": "8",
        "height": "1",
        "passthru": true,
        "outs": "all",
        "topic": "topic",
        "topicType": "msg",
        "min": 0,
        "max": "100",
        "step": 1,
        "x": 450,
        "y": 320,
        "wires": [
            [
                "3fd6667e1599e9e4"
            ]
        ]
    },
    {
        "id": "3fd6667e1599e9e4",
        "type": "change",
        "z": "c2d71647e91e29d4",
        "name": "",
        "rules": [
            {
                "t": "set",
                "p": "group_id",
                "pt": "msg",
                "to": "Slider",
                "tot": "str"
            }
        ],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": false,
        "x": 630,
        "y": 320,
        "wires": [
            [
                "8c17425cf6b74635"
            ]
        ]
    },
    {
        "id": "ce2d512e6bdde8c0",
        "type": "switch",
        "z": "c2d71647e91e29d4",
        "name": "",
        "property": "group_id",
        "propertyType": "msg",
        "rules": [
            {
                "t": "eq",
                "v": "Toggle",
                "vt": "str"
            }
        ],
        "checkall": "true",
        "repair": false,
        "outputs": 1,
        "x": 290,
        "y": 380,
        "wires": [
            [
                "58c095aeb88f64b9"
            ]
        ]
    },
    {
        "id": "07d15de2b9ae1137",
        "type": "change",
        "z": "c2d71647e91e29d4",
        "name": "",
        "rules": [
            {
                "t": "set",
                "p": "group_id",
                "pt": "msg",
                "to": "Toggle",
                "tot": "str"
            }
        ],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": false,
        "x": 630,
        "y": 380,
        "wires": [
            [
                "8c17425cf6b74635"
            ]
        ]
    },
    {
        "id": "58c095aeb88f64b9",
        "type": "ui_switch",
        "z": "c2d71647e91e29d4",
        "name": "",
        "label": "switch",
        "tooltip": "",
        "group": "f1fba85d.a4d008",
        "order": 1,
        "width": "3",
        "height": "1",
        "passthru": true,
        "decouple": "false",
        "topic": "topic",
        "topicType": "msg",
        "style": "",
        "onvalue": "true",
        "onvalueType": "bool",
        "onicon": "",
        "oncolor": "",
        "offvalue": "false",
        "offvalueType": "bool",
        "officon": "",
        "offcolor": "",
        "animate": false,
        "x": 450,
        "y": 380,
        "wires": [
            [
                "07d15de2b9ae1137"
            ]
        ]
    },
    {
        "id": "5594dc667bf68351",
        "type": "link out",
        "z": "c2d71647e91e29d4",
        "name": "link out 1",
        "mode": "link",
        "links": [
            "bd43089172c8d903"
        ],
        "x": 405,
        "y": 220,
        "wires": []
    },
    {
        "id": "bd43089172c8d903",
        "type": "link in",
        "z": "c2d71647e91e29d4",
        "name": "link in 1",
        "links": [
            "5594dc667bf68351"
        ],
        "x": 125,
        "y": 360,
        "wires": [
            [
                "7462ed6aed72ad5b",
                "ce2d512e6bdde8c0"
            ]
        ]
    },
    {
        "id": "8c17425cf6b74635",
        "type": "link out",
        "z": "c2d71647e91e29d4",
        "name": "link out 2",
        "mode": "link",
        "links": [
            "58808dd56afab92f"
        ],
        "x": 775,
        "y": 340,
        "wires": []
    },
    {
        "id": "58808dd56afab92f",
        "type": "link in",
        "z": "c2d71647e91e29d4",
        "name": "link in 2",
        "links": [
            "8c17425cf6b74635"
        ],
        "x": 595,
        "y": 220,
        "wires": [
            [
                "a7034deaa5ae9aea"
            ]
        ]
    },
    {
        "id": "b482e52067c1534d",
        "type": "inject",
        "z": "c2d71647e91e29d4",
        "name": "",
        "props": [
            {
                "p": "payload.x",
                "v": "",
                "vt": "date"
            },
            {
                "p": "topic",
                "vt": "str"
            }
        ],
        "repeat": ".5",
        "crontab": "",
        "once": false,
        "onceDelay": 0.1,
        "topic": "",
        "x": 290,
        "y": 440,
        "wires": [
            [
                "33b5676828edaa32"
            ]
        ]
    },
    {
        "id": "33b5676828edaa32",
        "type": "function",
        "z": "c2d71647e91e29d4",
        "name": "function 2",
        "func": "msg.payload.y = Math.floor(Math.random() * 101);\nmsg.group_id = \"Series\";\nreturn msg;",
        "outputs": 1,
        "timeout": 0,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 440,
        "y": 440,
        "wires": [
            [
                "8c17425cf6b74635",
                "daa355144a7489bd"
            ]
        ]
    },
    {
        "id": "cdb67b9d7a19c2e0",
        "type": "ui_chart",
        "z": "c2d71647e91e29d4",
        "name": "",
        "group": "f1fba85d.a4d008",
        "order": 2,
        "width": 0,
        "height": 0,
        "label": "chart",
        "chartType": "line",
        "legend": "false",
        "xformat": "payload.x",
        "interpolate": "linear",
        "nodata": "",
        "dot": false,
        "ymin": "0",
        "ymax": "100",
        "removeOlder": 1,
        "removeOlderPoints": "20",
        "removeOlderUnit": "3600",
        "cutout": 0,
        "useOneColor": false,
        "useUTC": false,
        "colors": [
            "#1f77b4",
            "#aec7e8",
            "#ff7f0e",
            "#2ca02c",
            "#98df8a",
            "#d62728",
            "#ff9896",
            "#9467bd",
            "#c5b0d5"
        ],
        "outputs": 1,
        "useDifferentColor": false,
        "x": 770,
        "y": 440,
        "wires": [
            []
        ]
    },
    {
        "id": "daa355144a7489bd",
        "type": "change",
        "z": "c2d71647e91e29d4",
        "name": "",
        "rules": [
            {
                "t": "set",
                "p": "payload",
                "pt": "msg",
                "to": "payload.y",
                "tot": "msg"
            }
        ],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": false,
        "x": 620,
        "y": 440,
        "wires": [
            [
                "cdb67b9d7a19c2e0"
            ]
        ]
    },
    {
        "id": "51845eb271625baa",
        "type": "websocket-listener",
        "path": "ws/mywebsocket/test",
        "wholemsg": "true"
    },
    {
        "id": "f1fba85d.a4d008",
        "type": "ui_group",
        "name": "Default",
        "tab": "c5a07d57.8efea8",
        "order": 1,
        "disp": true,
        "width": "11",
        "collapse": false
    },
    {
        "id": "c5a07d57.8efea8",
        "type": "ui_tab",
        "name": "Home",
        "icon": "dashboard",
        "order": 1,
        "disabled": false,
        "hidden": false
    }
]
```
Here's a section you can add to your `README.md` that describes the setup and usage for your Node-RED flow, specifically mentioning the need to adjust the external URL in `consumer.py` if there are any changes:

---

### Node-RED Flow Configuration

This Node-RED flow is designed to work with a WebSocket connection on port `1881` of a local server. The flow includes a slider, a switch, and a series of points displayed on a chart. Below is a summary of the components and their functions:

- **WebSocket Listener:** Listens on the path `/ws/mywebsocket/test` for incoming messages.
- **WebSocket Out:** Sends messages to the WebSocket server.
- **Slider:** A UI element for adjusting values, connected to a WebSocket.
- **Switch:** A UI element for toggling values, connected to a WebSocket.
- **Series:** Random points are generated and displayed on a chart, connected to a WebSocket.

The Node-RED flow is visualized as follows:

1. **WebSocket Input Node:** Listens to incoming messages and routes them based on the `group_id` to the appropriate UI element (Slider, Switch, or Series).
2. **Change Nodes:** Set the `group_id` to ensure the messages are routed correctly.
3. **Switch Nodes:** Filter messages based on their `group_id` to the correct output.

### Important Notice

This flow is configured to work on port `1881` of a local server. If you change the port or move the server to a different location, you must update the external URL in the `consumer.py` file of your Django application accordingly. 

For example, if the WebSocket server moves from `localhost:1881` to another IP or port, you need to update the WebSocket URL in `consumer.py`:

```python
websocket_url = "ws://<new_server_ip>:<new_port>/ws/mywebsocket/test"

```

Ensure that this URL matches the server's address and port for the WebSocket connection to function correctly.

---
