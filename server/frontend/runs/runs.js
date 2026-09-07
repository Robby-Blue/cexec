import * as time from "/time.js";

let runsContainer = document.getElementById("runs-container")

function showRuns(runs) {
    let lastDate = ""

    for (let run of runs) {
        let date = run.started_at.split(" ")[0]

        if (date != lastDate) {
            lastDate = date
            let dateElement = document.createElement("h2")
            dateElement.textContent = date
            runsContainer.appendChild(dateElement)
        }

        let container = document.createElement("div")
        container.classList.add("floating-container")
        container.classList.add("run-container")

        let headingElement = document.createElement("h3")
        let nameElement = document.createElement("a")
        nameElement.href = `/runs/${run.id}`
        nameElement.textContent = `#${run.id} - ${run.script}`
        headingElement.append(nameElement)
        container.append(headingElement)

        if (run.completed_at) {
            let exitElement = document.createElement("p")
            exitElement.textContent = `Exited with code ${run.exit_code}`
            container.append(exitElement)

            let formattedTime = time.formatTimespan(run.started_at, run.completed_at)

            let timeElement = document.createElement("p")
            timeElement.textContent = `Ran in ${formattedTime}`
            container.append(timeElement)
        }

        runsContainer.appendChild(container)
    }
}

async function getRunsData() {
    let r = await fetch("/api/runs")
    let data = await r.json()

    showRuns(data.reverse())
}

getRunsData()