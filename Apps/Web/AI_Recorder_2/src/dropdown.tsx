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
                if (step.sequence.toString() === meta_data['stepNo'].toString()) {
                    setSelectedValue(`Step ${(meta_data['stepNo']).toString()}: ${step.name || ''}`)
                }
            })
            fetchActionData(setActions)
        });
    },[stepNames])

    const handleMenuClick: MenuProps['onClick'] = async (e) => {
        const Step = stepNames.filter((step) => {
            if (step.sequence.toString() === e.key) {
                return step
            }
        })[0]

        let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
        let meta_data: metaDataInterface = localStorageMetadata.meta_data
        meta_data['stepNo'] = Step.sequence 
        meta_data['stepId'] = Step.id
        await browserAppData.storage.local.set({
            meta_data: meta_data,
        })
        setSelectedValue(`Step ${(Step?.sequence || 1).toString()}: ${Step?.name || ''}`)
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