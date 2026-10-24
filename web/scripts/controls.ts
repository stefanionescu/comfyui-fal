import { dynamicControlInputs } from '#web/nodes.ts';
import type { ComfyApp } from '@comfyorg/comfyui-frontend-types';

type HostNode = ComfyApp['rootGraph']['nodes'][number];
type HostWidget = NonNullable<HostNode['widgets']>[number];

/** A widget of ComfyUI, with the removal hook the published types do not describe. */
type Widget = HostWidget & { onRemove?: () => void };

/** A node of ComfyUI, with the custom values its dropdowns keep while they are on default. */
type CanvasNode = HostNode & {
    widgets?: Widget[];
    properties: HostNode['properties'] & { conditionalValues?: Record<string, Widget['value']> };
};

const controlRestorers = new WeakMap<CanvasNode, ((restore?: boolean) => void)[]>();

/**
 * Restore the value a child widget held under the current option, and save its value when the option leaves.
 *
 * Checked on frontend 1.49.6: ComfyUI resets a child widget to its default when its option returns.
 *
 * @param app - The ComfyUI app.
 * @param canvasNode - The node that owns the dropdown.
 * @param child - A widget the current option shows.
 * @param key - The current option and the name of the child, joined by a slash.
 * @param restore - Whether to put the saved value back.
 */
function keepChildValue(app: ComfyApp, canvasNode: CanvasNode, child: Widget, key: string, restore: boolean): void {
    const saved = canvasNode.properties.conditionalValues;

    if (restore && saved && Object.hasOwn(saved, key)) child.value = saved[key];
    const removed = child.onRemove?.bind(child);
    child.onRemove = () => {
        if (!app.configuringGraph) {
            canvasNode.properties.conditionalValues ??= {};

            canvasNode.properties.conditionalValues[key] = child.value;
        }
        removed?.();
    };
}

/**
 * Keep the values of the widgets a dropdown hides, in the properties of the node.
 *
 * @param app - The ComfyUI app.
 * @param canvasNode - The node that owns the dropdown.
 * @param widget - The dynamic dropdown.
 * @returns A callback that restores the widgets of the current option and watches new ones.
 */
function preserveControlValues(app: ComfyApp, canvasNode: CanvasNode, widget: Widget): (restore?: boolean) => void {
    const restoredWidgets = new WeakSet<Widget>();
    const restoreValues = (restore = false): void => {
        const selected = widget.value as string;
        for (const child of canvasNode.widgets ?? []) {
            if (!child.name.startsWith(`${widget.name}.`) || restoredWidgets.has(child)) continue;
            restoredWidgets.add(child);
            keepChildValue(app, canvasNode, child, `${selected}/${child.name}`, restore);
        }
    };
    restoreValues();
    return restoreValues;
}

/**
 * Restore the hidden values of a dropdown whenever its option changes, and redraw the Parameters panel.
 *
 * @param app - The ComfyUI app.
 * @param canvasNode - The node that owns the dropdown.
 * @param widget - The dynamic dropdown.
 * @returns The callback that restores the current option of this dropdown.
 */
function watchControl(app: ComfyApp, canvasNode: CanvasNode, widget: Widget): (restore?: boolean) => void {
    const restoreValues = preserveControlValues(app, canvasNode, widget);
    const previous = widget.callback?.bind(widget);
    widget.callback = (...args) => {
        previous?.(...args);
        restoreValues(true);
        // Checked on frontend 1.49.6: the Parameters panel keeps the rows of the previous option until the selection changes.
        // eslint-disable-next-line @typescript-eslint/no-deprecated -- reason: ComfyUI offers no other way to refresh the Parameters panel.
        app.canvas.onSelectionChange?.(app.canvas.selected_nodes);
    };
    return restoreValues;
}

/**
 * Keep the custom values of a new node across its option changes.
 *
 * @param app - The ComfyUI app.
 * @param canvasNode - The node ComfyUI created.
 */
export function addNodeControls(app: ComfyApp, canvasNode: CanvasNode): void {
    const restorers: ((restore?: boolean) => void)[] = [];
    for (const name of dynamicControlInputs.get(canvasNode.comfyClass ?? '') ?? []) {
        const widget = canvasNode.widgets?.find((candidate) => candidate.name === name);
        if (widget) restorers.push(watchControl(app, canvasNode, widget));
    }
    controlRestorers.set(canvasNode, restorers);
}

/**
 * Watch the custom values of every node after ComfyUI loads a graph.
 *
 * @param app - The ComfyUI app.
 */
export function refreshGraph(app: ComfyApp): void {
    for (const canvasNode of app.rootGraph.nodes) {
        for (const restoreValues of controlRestorers.get(canvasNode) ?? []) restoreValues();
    }
}
