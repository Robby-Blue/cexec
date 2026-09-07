let path = window.location.pathname.slice("/files/".length)

let needsSlash = !window.location.pathname.endsWith("/")
let linkSlash = needsSlash ? "/" : ""

let pathName = `${window.location.pathname}${linkSlash}`



function elementSetText(element_id, text) {
    let element = document.getElementById(element_id)
    element.textContent = text
}

function showFolderContents(children) {
    let folderContainer = document.getElementById("folder-container")
    folderContainer.classList.remove("gone")

    let childrenContainer = document.getElementById("children-container")

    for (let child of children) {
        let nameSuffix = child.is_folder ? "/" : ""
        let displayName = `${child.name}${nameSuffix}`

        let pElement = document.createElement("p")
        let linkElement = document.createElement("a")
        linkElement.textContent = displayName
        linkElement.href = `${pathName}${child.name}`
        pElement.appendChild(linkElement)

        childrenContainer.appendChild(pElement)
    }
}

function showFileContents() {
    let folderContainer = document.getElementById("file-container")
    folderContainer.classList.remove("gone")

    let downloadUrl = `/api/files/download/${path}`

    let downloadButton = document.getElementById("download-button")
    downloadButton.href = downloadUrl
}

async function getFileInfo() {
    let r = await fetch(`/api/files/info/${path}`)
    let data = await r.json()

    if (data.type == "folder") {
        showFolderContents(data.children)
    }
    if (data.type == "file") {
        showFileContents()
    }
}

elementSetText("heading", `Files - /${path}`)

let backButton = document.getElementById("back-button")
let lastSlashIndex = pathName.lastIndexOf("/", pathName.length - 2)
let parentFolder = pathName.slice(0, lastSlashIndex + 1)
backButton.href = parentFolder

if (parentFolder == "/") {
    backButton.classList.add("hidden")
    backButton.classList.remove("button")
    // .buttons cant be hidden bc css sillyness, at least
    // not without making the css so much more complicated
}

document.title = `Files - /${path}`

getFileInfo()