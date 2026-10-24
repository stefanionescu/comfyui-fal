/** The fal nodes whose number settings show a value on custom, and those settings, in node order. */
export const dynamicControlInputs: ReadonlyMap<string, readonly string[]> = new Map([
    ['FalImageGenerate', ['num_images', 'guidance_scale', 'num_inference_steps', 'seed']],
    ['FalVideoGenerate', ['duration', 'seed']],
    ['FalAudioGenerate', ['seed']],
]);
