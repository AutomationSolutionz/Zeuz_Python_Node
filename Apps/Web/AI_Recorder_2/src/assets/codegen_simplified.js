class codeGen {
    isRangeInput(target) {
        if (!target || target.nodeName !== 'INPUT')
            return false;
        return target.type.toLowerCase() === 'range';
    }
    asCheckbox(target) {
        if (!target || target.nodeName !== 'INPUT')
            return null;
        return ['checkbox', 'radio'].includes(target.type) ? target : null;
    }
    _shouldIgnoreMouseEvent(event) {
        const target = event.target;
        const nodeName = target.nodeName;
        if (nodeName === 'SELECT' || nodeName === 'OPTION')
            return true;
        if (nodeName === 'INPUT' && ['date', 'range'].includes(target.type))
            return true;
        return false;
    }
    _shouldGenerateKeyPressFor(event) {
        // Enter aka. new line is handled in input event.
        if (event.key === 'Enter' && (event.target.nodeName === 'TEXTAREA' || event.target.isContentEditable))
            return false;
        // Backspace, Delete, AltGraph are changing input, will handle it there.
        if (['Backspace', 'Delete', 'AltGraph'].includes(event.key))
            return false;
        // Ignore the QWERTZ shortcut for creating a at sign on MacOS
        if (event.key === '@' && event.code === 'KeyL')
            return false;
        // Allow and ignore common used shortcut for pasting.
        if (navigator.platform.includes('Mac')) {
            if (event.key === 'v' && event.metaKey)
                return false;
        } else {
            if (event.key === 'v' && event.ctrlKey)
                return false;
            if (event.key === 'Insert' && event.shiftKey)
                return false;
        }
        if (['Shift', 'Control', 'Meta', 'Alt', 'Process'].includes(event.key))
            return false;
        const hasModifier = event.ctrlKey || event.altKey || event.metaKey;
        if (event.key.length === 1 && !hasModifier)
            return !!this.asCheckbox(event.target);
        return true;
    }
    onClick(event) {
        // in webkit, sliding a range element may trigger a click event with a different target if the mouse is released outside the element bounding box.
        // So we check the hovered element instead, and if it is a range input, we skip click handling
        if (this.isRangeInput(event.target))
            return;
        if (this._shouldIgnoreMouseEvent(event))
            return;

        const checkbox = this.asCheckbox(event.target);
        if (checkbox) {
            // Interestingly, inputElement.checked is reversed inside this event handler.
            this._performAction({
                name: checkbox.checked ? 'check' : 'uncheck',
                selector: selector,
                signals: [],
            });
            return;
        }

        this._performAction({
            name: 'click',
            selector: selector,
            position: positionForEvent(event),
            signals: [],
            button: buttonForEvent(event),
            modifiers: modifiersForEvent(event),
            clickCount: event.detail
        });
    }

    onFocus(event) {
        this._onFocus(true);
    }

    onInput(event) {
        const target = event.target;

        if (target.nodeName === 'INPUT' && target.type.toLowerCase() === 'file') {
            this.delegate.recordAction?.({
                name: 'setInputFiles',
                selector: selector,
                signals: [],
                files: [...(target.files || [])].map(file => file.name),
            });
            return;
        }

        if (this.isRangeInput(target)) {
            this.delegate.recordAction?.({
                name: 'fill',
                // must use hoveredModel instead of activeModel for it to work in webkit
                selector: selector,
                signals: [],
                text: target.value,
            });
            return;
        }

        if (['INPUT', 'TEXTAREA'].includes(target.nodeName) || target.isContentEditable) {
            if (target.nodeName === 'INPUT' && ['checkbox', 'radio'].includes(target.type.toLowerCase())) {
                // Checkbox is handled in click, we can't let input trigger on checkbox - that would mean we dispatched click events while recording.
                return;
            }
            this.delegate.recordAction?.({
                name: 'fill',
                selector: selector,
                signals: [],
                text: target.isContentEditable ? target.innerText : target.value,
            });
        }

        if (target.nodeName === 'SELECT') {
            const selectElement = target;
            this._performAction({
                name: 'select',
                selector: selector,
                options: [...selectElement.selectedOptions].map(option => option.value),
                signals: []
            });
        }
    }

    onKeyDown(event) {
        if (!this._shouldGenerateKeyPressFor(event))
            return;
        // Similarly to click, trigger checkbox on key event, not input.
        if (event.key === ' ') {
            const checkbox = this.asCheckbox(event.target);
            if (checkbox) {
                this._performAction({
                    name: checkbox.checked ? 'uncheck' : 'check',
                    selector: selector,
                    signals: [],
                });
                return;
            }
        }

        this._performAction({
            name: 'press',
            selector: selector,
            signals: [],
            key: event.key,
            modifiers: modifiersForEvent(event),
        });
    }

    onKeyUp(event) {
        if (!this._shouldGenerateKeyPressFor(event))
            return;
    }
}