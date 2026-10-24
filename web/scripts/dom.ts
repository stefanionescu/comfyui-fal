/**
 * Create a typed element and insert optional text safely.
 *
 * @param tag - The HTML tag to create.
 * @param text - Plain text content; leave it out for an element without text.
 * @returns The new element.
 */
export function element<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string): HTMLElementTagNameMap[K] {
    const node = document.createElement(tag);
    if (text !== undefined) node.append(document.createTextNode(text));
    return node;
}

/**
 * Create a button with an explicit form behavior.
 *
 * @param text - The visible button label.
 * @param type - Whether the button submits its form.
 * @returns The new button.
 */
export function button(text: string, type: 'button' | 'submit' = 'button'): HTMLButtonElement {
    const node = element('button', text);
    node.type = type;
    return node;
}
