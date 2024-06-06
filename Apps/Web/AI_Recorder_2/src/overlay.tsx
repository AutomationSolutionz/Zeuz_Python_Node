import React from "react"
import { CloseCircleOutlined, LoadingOutlined, CheckCircleOutlined } from "@ant-design/icons"
interface overlayInerface {
    setShowOverlay: (x: boolean) => void,
}
const AI_texts = [
    {
        text: 'Analyzing HTML structure',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Evaluating element attributes',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Checking text content spelling',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Identifying meaningful word patterns',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Checking for unique element identifiers',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Analyzing surrounding parent-siblings-children',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Detecting element relationships',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Handling dynamic content',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Comparing similar elements to ensure accuracy',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Filtering out random characters from text content',
        time: (Math.random() * 3 + 0.5) * 1000
    },
    {
        text: 'Constructing optimized XPath expression',
        time: (Math.random() * 1 + 4) * 1000
    },
    {
        text: 'Converting xpath to ZeuZ action',
        time: (Math.random() * 1 + 5) * 1000
    }
];
const Overlay = ({ setShowOverlay }: overlayInerface) => {
    return (
        <div className="overlay d-flex flex-column justify-content-center align-items-center px-3">
            <div className="overlay-uppernav d-flex justify-content-between my-3">
                <div className="overlay-title title">Smart Processing...</div>
                <CloseCircleOutlined
                    onClick={() => setShowOverlay(false)}
                    className="overlay-close"
                />
            </div>
            <img className="overlay-gif rounded-circle" src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGtsc2hyZTVpMTlzcWgzdGU4bTN4bmhxcWJ3b292ejJ3YmdreG1rbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/7VzgMsB6FLCilwS30v/giphy.webp" alt="" />
            <div className="overlay-content d-flex-column justify-content-start my-4">
                {
                    AI_texts.map(({ text, time }) => (
                        <AIText text={text} time={time} />
                    ))
                }
            </div>

        </div>
    )
}
export default Overlay

const AIText = ({ text, time }: { text: string, time: number }) => {
    const [finished, setFinished] = React.useState(false)
    React.useEffect(() => {
        const timer = setTimeout(() => {
            setFinished(true)
        }, time)
        return () => clearTimeout(timer)
    }, [])
    return (
        <div className="d-flex justify-content-start mb-1">
            <div className="overlay-text" style={{ opacity: finished ? 1 : 0.5 }}>{text}</div>
            <div className="overlay-icon ml-2">
                {finished ? <CheckCircleOutlined className="overlay-icon-check" /> : <LoadingOutlined className="overlay-icon-loading" />}
            </div>
        </div>
    )
}