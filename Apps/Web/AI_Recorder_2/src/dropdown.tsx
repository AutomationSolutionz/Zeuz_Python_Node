import React from 'react';
import { useState, useEffect } from 'react';
import type { MenuProps } from 'antd';
import { Button, Dropdown, message, Space, Tooltip } from 'antd';
import { stepZsvc, fetchActionData, browserAppData, actionsInterface, metaDataInterface } from './common';
interface stepNamesInterface {
    stepNames: stepZsvc[],
    setActions: (f: () => actionsInterface) => void,
}

const dropdown = ({ stepNames, setActions }: stepNamesInterface) => {
    const [selectedValue, setSelectedValue] = useState<string>('Loading...');

    useEffect(() => {
        browserAppData.storage.local.get('meta_data', (localStorageMetadata)=>{
            let meta_data: metaDataInterface = localStorageMetadata.meta_data
            stepNames.map((step) => {
                console.log(step.sequence.toString(), meta_data['stepNo'].toString(), step.sequence.toString() === meta_data['stepNo'].toString())
                if (step.sequence.toString() === meta_data['stepNo'].toString()) {
                    setSelectedValue(`Step ${(meta_data['stepNo']).toString()}: ${step.name || ''}`)
                }
            })
            console.log('Fetch Action call from dropdown init')
            fetchActionData(setActions)
        });
    },[stepNames])

    const handleMenuClick: MenuProps['onClick'] = async (e) => {
        console.log('select-event', e);
        const Step = stepNames.filter((step) => {
            console.log(step.sequence.toString(), e.key, step.sequence.toString() === e.key)
            if (step.sequence.toString() === e.key) {
                return step
            }
        })[0]

        let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
        let meta_data: metaDataInterface = localStorageMetadata.meta_data
        meta_data['stepNo'] = Step?.sequence || 1
        await browserAppData.storage.local.set({
            meta_data: meta_data,
        })
        console.log(`Step ${(Step?.sequence || 1).toString()}: ${Step?.name || ''}`)
        console.log('step', Step)
        setSelectedValue(`Step ${(Step?.sequence || 1).toString()}: ${Step?.name || ''}`)
        console.log('Fetch Action call from dropdown click-handle')
        fetchActionData(setActions)
    };

    const items: MenuProps['items'] = stepNames.map((step) => {
        return {
            label: step.name,
            key: step.sequence.toString(),
        };
    })

    return (
        <Dropdown
            menu={{
                items,
                onClick: handleMenuClick,
            }}
        // arrow={false}
        >
            <a onClick={(e) => e.preventDefault()} style={{ cursor: 'default' }}>
                {/* <Space> */}
                {selectedValue}
                {/* <DownOutlined /> */}
                {/* </Space> */}
            </a>
        </Dropdown>
    );
};
export default dropdown;