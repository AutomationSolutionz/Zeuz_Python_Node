function emptyNode(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}

function assignChildNodes(dest, src, clone, deep) {
    emptyNode(dest);
    appendChildNodes(dest, src, clone, deep);
}

function appendChildNodes(dest, src, clone, deep) {
    if (clone) {
        let children = src.childNodes;
        for (let i = 0; i < children.length; i++) {
            dest.appendChild(children[i].cloneNode(deep));
        }
    } else {
        while(src.firstChild) {
            dest.appendChild(src.firstChild);
        }
    }
}
