import * as time from "/time.js";

function elementSetText(element_id, text) {
    let element = document.getElementById(element_id)
    element.textContent = text
}

let index = window.location.pathname.slice("/runs/".length)

let filesButton = document.getElementById("files-button")
filesButton.href = `/files/runs/${index}`

elementSetText("heading", `Run #${index}`)
document.title = `Run #${index}`

async function getRunData() {
    let r = await fetch(`/api/runs/${index}`)
    let data = await r.json()

    elementSetText("script-cell", data.script)
    elementSetText("tag-cell", data.tag)
    elementSetText("started-cell", data.started_at)
    elementSetText("completed-cell", data.completed_at)
    let runtime = time.formatTimespan(data.started_at, data.completed_at)
    elementSetText("runtime-cell", runtime)

    elementSetText("exit-cell", data.exit_code)
}

getRunData()