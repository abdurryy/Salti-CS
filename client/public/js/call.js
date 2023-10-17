const server_api_url = "http://192.168.1.123:3001/";

async function status() {
    try {
        const response = await fetch("http://192.168.1.123:3001/status", {
            method: "GET",
            mode: "cors",
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data.in_call);
    } catch (error) {
        console.error(error);
    }
}

status();
