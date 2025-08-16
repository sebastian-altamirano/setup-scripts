interface FilePickerAcceptType {
	accept: Record<string, string[]>;
	description?: string;
}

interface FilePickerOptions {
	excludeAcceptAllOption?: boolean;
	id?: string;
	multiple?: boolean;
	startIn?:
		| FileSystemHandle
		| "desktop"
		| "documents"
		| "downloads"
		| "music"
		| "pictures"
		| "videos";
	types?: FilePickerAcceptType[];
	description?: string;
}

declare global {
	interface Window {
		showOpenFilePicker?: (
			options?: FilePickerOptions,
		) => Promise<[FileSystemFileHandle, ...FileSystemFileHandle[]]>;
	}
}

export {};
