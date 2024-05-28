// import {Helmet} from "react-helmet";
import {DeleteOutlined} from '@ant-design/icons'
import type {actionType} from './common'
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
            <div className={"action py-3 pl-3 mb-1 d-flex align-item-center" + (action.animateRomove? ' animExit' : '')}>
                {/* <div><img className="d-inline-block zeuz-icon" src="../small_logo.png" alt=""/></div> */}
                <div className="d-inline-block pl-2 pr-4">{idx+1}</div>
                <div className={"action-text "+ (action.typeWrite ? "typing-demo" : "")} onAnimationEnd={handeAnimationEnd} >{(action==undefined) ? 'Loading...' : action.name}</div>
                <div className="del-button py-0 ml-auto mr-3" onClick={handeOnRemove}>
                    {/* <img src="trash.svg" alt="" height={14} width={14} className="trash-icon"/>
                    <span className="visually-hidden">Button</span> */}
                    <DeleteOutlined />
                </div>
            </div>
        </>)
    )
}

