const server_api_url = "http://192.168.1.124:3001/";
const status_speed = 1000;


async function status() {
    try {
        const response = await fetch(`${server_api_url}status`, {
            method: "GET",
            mode: "cors",
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        callbtn = document.getElementById("call_btn")
        hangupbtn = document.getElementById("hangup_ctn")
        hangupgtn = document.getElementById("hangup_btn")
        if (data.in_call == true) {
            target = data.call_server_dict.number;
            color = "";
            if (data.call_server_dict.status == 1){
                msg = `CURRENTLY CALLING ${target}`; 
                color = "orange";
                hangupgtn.innerHTML = `STOP`;

            } else if (data.call_server_dict.status == 2){
                msg = `CURRENTLY IN CALL WITH ${target}`;
                hangupbtn.style.display = "flex";
                hangupgtn.innerHTML = `HANG UP`;
                color = "green";
            } else if (data.call_server_dict.status == 3){
                msg = `${target} DECLINED THE CALL`;
                color = "red";
            } else {
                msg =`CALL IN QUEUE`;
                color = "yellow";
            }
            
            callbtn.disabled = true;
            callbtn.style.backgroundColor = "grey";
            
        } else {
            callbtn.disabled = false;
            hangupbtn.style.display = "none";
            callbtn.style.backgroundColor = "#58ff90";
        }
        document.getElementById("status").innerHTML =  + data.in_call == false ? "SERVER STATUS: <span style='color:green;'>NOT IN A CALL </span" : `SERVER STATUS: <span style='color:${color};'>${msg}</span>`;
    } catch (error) {
        console.error(error);
    }
}

async function hangup() {
    try {
        const response = await fetch(`${server_api_url}hangup`, {
            method: "GET",
            mode: "cors",
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}

async function call() {
    try {
        number = document.getElementById("number").value;
        const response = await fetch(`${server_api_url}call/${number}`, {
            method: "GET",
            mode: "cors",
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        if (data.status == "failure"){
            document.getElementById("popup").style.display = "flex";
        }
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}

setInterval(() => {
    status(); 
}, status_speed);

