import React, { useRef, useEffect } from "react"
import './App.css'
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
            <AnimatedIcon />
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

const AnimatedIcon: React.FC = () => {
    const pathRef = useRef<SVGPathElement>(null);

    useEffect(() => {
        const startAnimation = () => {
            if (pathRef.current) {
                pathRef.current.style.fill = 'url(#animatedGradient)';
            }
        };

        const stopAnimation = () => {
            if (pathRef.current) {
                pathRef.current.style.fill = 'url(#fixedGradient)';
            }
        };

        const longRunningFunction = async () => {
            startAnimation();
            await new Promise(resolve => setTimeout(resolve, 5000)); // Simulate delay
            stopAnimation();
        };

        longRunningFunction();
    }, []);

    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            xmlnsXlink="http://www.w3.org/1999/xlink"
            version="1.1"
            width="170"
            height="170"
            viewBox="400 300 1400 1400"
            xmlSpace="preserve"
        >
            <desc>Created with Fabric.js 5.2.4</desc>
            <defs>
                <linearGradient id="animatedGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="rgb(255, 255, 255)">
                        <animate attributeName="stop-color" values="#43cea2; #980045; #185a9d; #43cea2" dur="5s" repeatCount="indefinite" />
                    </stop>
                    <stop offset="100%" stop-color="rgb(255, 255, 255)">
                        <animate attributeName="stop-color" values="#185a9d; #43cea2; #980045; #185a9d" dur="5s" repeatCount="indefinite" />
                    </stop>
                </linearGradient>
                <linearGradient id="fixedGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{ stopColor: '#43cea2', stopOpacity: 1 }} />
                    <stop offset="100%" style={{ stopColor: '#185a9d', stopOpacity: 1 }} />
                </linearGradient>
            </defs>
            <g transform="matrix(8.7 0 0 8.7 540 540)">
                <path
                    ref={pathRef}
                    style={{ fill: 'url(#animatedGradient)' }}
                    d="M 79.3 30.2 C 85.39999999999999 30.2 90.3 25.299999999999997 90.3 19.2 C 90.3 13.1 85.39999999999999 8.2 79.3 8.2 C 73.2 8.2 68.3 13.1 68.3 19.2 C 68.3 22.099999999999998 69.5 24.799999999999997 71.3 26.799999999999997 L 57.9 41 C 55.9 39.1 53.199999999999996 37.9 50.3 37.9 C 47.4 37.9 44.699999999999996 39 42.8 40.9 L 29.4 28.6 C 30.299999999999997 27.400000000000002 30.799999999999997 25.900000000000002 30.799999999999997 24.3 C 30.799999999999997 20.3 27.499999999999996 17 23.499999999999996 17 C 19.499999999999996 17 16.199999999999996 20.3 16.199999999999996 24.3 C 16.199999999999996 28.3 19.499999999999996 31.6 23.499999999999996 31.6 C 25.399999999999995 31.6 27.099999999999998 30.900000000000002 28.4 29.700000000000003 L 41.8 42 C 40.3 43.9 39.4 46.3 39.4 48.9 C 39.4 51.8 40.5 54.4 42.3 56.3 L 27.5 71.9 C 25.6 70.30000000000001 23.2 69.4 20.5 69.4 C 14.4 69.4 9.5 74.30000000000001 9.5 80.4 C 9.5 86.5 14.4 91.4 20.5 91.4 C 26.6 91.4 31.5 86.5 31.5 80.4 C 31.5 77.5 30.4 74.9 28.6 73 L 43.3 57.4 C 45.199999999999996 59 47.599999999999994 59.9 50.3 59.9 C 50.5 59.9 50.599999999999994 59.9 50.8 59.9 L 52.699999999999996 76.9 C 48.699999999999996 77.7 45.599999999999994 81.2 45.599999999999994 85.5 C 45.599999999999994 90.4 49.49999999999999 94.3 54.39999999999999 94.3 C 59.29999999999999 94.3 63.19999999999999 90.39999999999999 63.19999999999999 85.5 C 63.19999999999999 80.6 59.29999999999999 76.7 54.39999999999999 76.7 C 54.29999999999999 76.7 54.19999999999999 76.7 54.099999999999994 76.7 L 52.199999999999996 59.7 C 54.8 59.2 57.099999999999994 57.900000000000006 58.699999999999996 55.900000000000006 L 72.3 65.7 C 71.7 66.8 71.3 68 71.3 69.4 C 71.3 73.4 74.6 76.7 78.6 76.7 C 82.6 76.7 85.89999999999999 73.4 85.89999999999999 69.4 C 85.89999999999999 65.4 82.6 62.10000000000001 78.6 62.10000000000001 C 76.39999999999999 62.10000000000001 74.5 63.10000000000001 73.19999999999999 64.60000000000001 L 59.59999999999999 54.80000000000001 C 60.69999999999999 53.10000000000001 61.29999999999999 51.10000000000001 61.29999999999999 49.000000000000014 C 61.29999999999999 46.40000000000001 60.39999999999999 44.100000000000016 58.89999999999999 42.20000000000002 L 72.39999999999999 27.900000000000016 C 74.3 29.3 76.7 30.2 79.3 30.2 z"
                />
            </g>
        </svg>
    );
};
