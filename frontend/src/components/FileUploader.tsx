"use client";

import React, { useCallback, useState } from "react";

interface FileUploaderProps {
    onFileSelect: (file: File) => void;
    isLoading: boolean;
}

export default function FileUploader({ onFileSelect, isLoading }: FileUploaderProps) {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
        else if (e.type === "dragleave") setDragActive(false);
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            e.stopPropagation();
            setDragActive(false);
            if (e.dataTransfer.files?.[0]) {
                const file = e.dataTransfer.files[0];
                setSelectedFile(file);
                onFileSelect(file);
            }
        },
        [onFileSelect]
    );

    const handleFileInput = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files?.[0]) {
                const file = e.target.files[0];
                setSelectedFile(file);
                onFileSelect(file);
            }
        },
        [onFileSelect]
    );

    return (
        <div
            id="file-uploader"
            className={`relative rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-300 cursor-pointer ${dragActive
                    ? "border-[var(--primary)] bg-[var(--primary)]/10 scale-[1.02]"
                    : "border-[var(--border)] hover:border-[var(--primary-light)] hover:bg-[var(--card-hover)]"
                } ${isLoading ? "pointer-events-none opacity-60" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-input")?.click()}
        >
            <input
                id="file-input"
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileInput}
                className="hidden"
                disabled={isLoading}
            />

            {/* Icon */}
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[var(--primary)]/15">
                <svg
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="var(--primary-light)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
            </div>

            {selectedFile ? (
                <div>
                    <p className="text-lg font-semibold text-[var(--foreground)]">
                        {selectedFile.name}
                    </p>
                    <p className="mt-1 text-sm text-[var(--muted)]">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                </div>
            ) : (
                <div>
                    <p className="text-lg font-medium text-[var(--foreground)]">
                        Drag & drop your CV here
                    </p>
                    <p className="mt-2 text-sm text-[var(--muted)]">
                        or click to browse · PDF, DOCX, TXT
                    </p>
                </div>
            )}
        </div>
    );
}
