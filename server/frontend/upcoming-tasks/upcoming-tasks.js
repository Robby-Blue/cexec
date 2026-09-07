let tasksContainer = document.getElementById("tasks-container")

function showTasks(tasks) {
    let lastDate = ""

    for (let task of tasks) {
        if (task.started_at) {
            continue
        }
        let date = task.created_at.split(" ")[0]

        if (date != lastDate) {
            lastDate = date
            let dateElement = document.createElement("h2")
            dateElement.textContent = date
            tasksContainer.appendChild(dateElement)
        }

        let container = document.createElement("div")
        container.classList.add("floating-container")
        container.classList.add("task-container")

        let headingElement = document.createElement("h3")
        headingElement.textContent = `#${task.id} - ${task.script}`
        container.append(headingElement)

        tasksContainer.appendChild(container)
    }
}

async function getTasksData() {
    let r = await fetch("/api/tasks")
    let data = await r.json()

    showTasks(data.reverse())
}

getTasksData()