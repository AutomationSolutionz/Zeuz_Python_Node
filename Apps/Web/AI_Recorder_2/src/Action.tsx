// import {Helmet} from "react-helmet";
export type actionType ={
    id: string,
    stillRecording: Boolean,
    is_disable: boolean,
    main: string[][],
    name: string,
    typeWrite: boolean,
    animateRomove: boolean,
    short:{
        action: string,
        element: string,
        value: string,
    },
    xpath: string
}
interface actionInterface{
    action: actionType
    idx: number
    removeAction: (index:number[], animate:Boolean) => void
    animationRemove: (index:number) => void
}

export function Action({action, idx, removeAction, animationRemove}: actionInterface) {
    const handeOnRemove = ()=>{
        removeAction([idx], false)
    }
    const handeAnimationEnd = ()=>{
        animationRemove(idx)
    }
    return (
        action.stillRecording ? <></> : (
        <>
            <div className={"action py-2 pl-3 mb-1 d-flex align-item-center bd-highlight " + (action.animateRomove? 'animExit' : '')}>
                <div><img className="d-inline-block zeuz-icon" src="../small_logo.png" alt=""/></div>
                <div className="d-inline-block pl-2 pr-4">{idx+1}</div>
                <div className={"action-text "+ (action.typeWrite ? "typing-demo" : "")} onAnimationEnd={handeAnimationEnd} >{(action==undefined) ? 'Loading...' : action.name}</div>
                <button type="button" className="btn btn-outline-danger btn-sm py-0 px-1 ml-auto mr-2 bd-highlight" onClick={handeOnRemove}>
                    <img src="trash.svg" alt="" height={14} width={14} className="trash-icon"/>
                    <span className="visually-hidden">Button</span>
                </button>
            </div>
        </>)
    )
}

