# Node-RED + JeeG

**Node-RED calls JeeG:** start Node-RED with the token in its environment (so it is not stored in the flow), on the same
computer as JeeG:

    export JEEG_TOKEN=$(jeeg --api-token)      (Windows: set JEEG_TOKEN=...  then start node-red)
    node-red

Menu > Import > paste `jeeg-flow.json`. Click the *Ask JeeG* inject button; the answer shows in the debug sidebar.
Change the inject text, or feed any text into *Build JeeG request*.

**JeeG calls Node-RED:** the flow includes an *http in* node at `POST /jeeg`. Then in JeeG:

    rest add nodered http://127.0.0.1:1880 none
    rest post nodered /jeeg {"event":"door opened"}
