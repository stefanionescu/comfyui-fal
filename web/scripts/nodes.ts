/** The fal nodes whose dropdowns show a value on custom, and those dropdowns, in node order. */
export const dynamicControlInputs: ReadonlyMap<string, readonly string[]> = new Map([
    [
        'FalImageGenerate',
        ['aspect_ratio', 'resolution', 'num_images', 'output_format', 'guidance_scale', 'num_inference_steps', 'seed'],
    ],
    ['FalVideoGenerate', ['duration', 'resolution', 'aspect_ratio', 'generate_audio', 'seed']],
    ['FalAudioGenerate', ['output_format', 'seed']],
]);
