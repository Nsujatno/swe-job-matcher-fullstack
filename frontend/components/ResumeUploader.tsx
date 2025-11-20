"use client";

import { useState, useRef, ChangeEvent, DragEvent } from "react";
import {
	UploadCloud,
	FileText,
	X,
	CheckCircle,
	AlertCircle,
	Loader2,
} from "lucide-react";
import { useAuth } from "@clerk/nextjs";

type UploadStatus = "idle" | "uploading" | "success" | "error";

export default function ResumeUploader() {
	const { getToken } = useAuth();
	const [file, setFile] = useState<File | null>(null);
	const [isDragging, setIsDragging] = useState(false);
	const [status, setStatus] = useState<UploadStatus>("idle");
	const [errorMessage, setErrorMessage] = useState<string>("");

	// hidden input reference
	const fileInputRef = useRef<HTMLInputElement>(null);

	// Configuration
	const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
	const ALLOWED_TYPES = ["application/pdf"];

	const validateFile = (file: File): boolean => {
		if (!ALLOWED_TYPES.includes(file.type)) {
			setErrorMessage("Only PDF files are allowed.");
			setStatus("error");
			return false;
		}
		if (file.size > MAX_FILE_SIZE) {
			setErrorMessage("File size must be less than 5MB.");
			setStatus("error");
			return false;
		}
		return true;
	};

	const handleFileSelect = (selectedFile: File) => {
		setErrorMessage("");
		setStatus("idle");

		if (validateFile(selectedFile)) {
			setFile(selectedFile);
		}
	};

	// --- Event Handlers ---

	const onDragOver = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		setIsDragging(true);
	};

	const onDragLeave = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		setIsDragging(false);
	};

	const onDrop = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		setIsDragging(false);

		if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
			handleFileSelect(e.dataTransfer.files[0]);
			// Reset input value so same file can be selected again if needed
			if (fileInputRef.current) fileInputRef.current.value = "";
		}
	};

	const onFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
		if (e.target.files && e.target.files.length > 0) {
			handleFileSelect(e.target.files[0]);
		}
	};

	const handleRemoveFile = () => {
		setFile(null);
		setStatus("idle");
		setErrorMessage("");
	};

	const handleUpload = async () => {
		if (!file) return;

		setStatus("uploading");

		// --- TODO: CONNECT TO YOUR BACKEND HERE ---
		try {
			const token = await getToken();
			const formData = new FormData();
			formData.append("file", file);
			const response = await fetch("http://localhost:8000/api/upload-resume", {
				method: "POST",
				headers: {
					Authorization: `Bearer ${token}`,
				},
				body: formData,
			});
			if (response.status == 401) {
				setErrorMessage("Make sure to sign in first");
			}
			if (!response.ok) {
				throw new Error("Failed to upload resume");
			}
			setStatus("success");
		} catch (error) {
			console.error(error);
			setStatus("error");
			if (!errorMessage) {
				setErrorMessage("Something went wrong uploading your resume.");
			}
		}
	};

	return (
		<div className="w-full max-w-xl mx-auto">
			{/* Drop Zone */}
			<div
				className={`
          relative border-2 border-dashed rounded-2xl p-8 transition-all duration-300 ease-in-out text-center cursor-pointer
          ${
											isDragging
												? "border-indigo-500 bg-indigo-500/10"
												: "border-slate-700 bg-slate-800/50 hover:bg-slate-800"
										}
          ${status === "error" ? "border-red-500/50 bg-red-500/5" : ""}
        `}
				onDragOver={onDragOver}
				onDragLeave={onDragLeave}
				onDrop={onDrop}
				onClick={() => fileInputRef.current?.click()}
			>
				<input
					type="file"
					ref={fileInputRef}
					className="hidden"
					accept=".pdf"
					onChange={onFileInputChange}
				/>

				{/* IDLE STATE: No file selected */}
				{!file && (
					<div className="space-y-4">
						<div className="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto text-indigo-400">
							<UploadCloud size={32} />
						</div>
						<div>
							<p className="text-lg font-semibold text-white">
								Click to upload or drag and drop
							</p>
							<p className="text-sm text-slate-400 mt-1">PDF (max 5MB)</p>
						</div>
					</div>
				)}

				{/* SELECTED STATE: File is present */}
				{file && (
					<div className="flex items-center justify-between bg-slate-700/50 p-4 rounded-xl border border-slate-600">
						<div className="flex items-center gap-3 overflow-hidden">
							<div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">
								<FileText size={24} />
							</div>
							<div className="text-left min-w-0">
								<p className="text-sm font-medium text-white truncate max-w-[200px]">
									{file.name}
								</p>
								<p className="text-xs text-slate-400">
									{(file.size / 1024 / 1024).toFixed(2)} MB
								</p>
							</div>
						</div>

						{status !== "uploading" && status !== "success" && (
							<button
								onClick={(e) => {
									e.stopPropagation();
									handleRemoveFile();
								}}
								className="p-1.5 hover:bg-slate-600 rounded-full text-slate-400 hover:text-white transition-colors"
							>
								<X size={20} />
							</button>
						)}
					</div>
				)}
			</div>

			{/* Error Message */}
			{errorMessage && (
				<div className="flex items-center gap-2 mt-4 text-red-400 bg-red-400/10 p-3 rounded-lg text-sm border border-red-400/20">
					<AlertCircle size={16} />
					{errorMessage}
				</div>
			)}

			{/* Action Button */}
			{file && status !== "success" && (
				<button
					onClick={handleUpload}
					disabled={status === "uploading"}
					className={`
            mt-6 w-full py-3.5 rounded-xl font-semibold transition-all flex items-center justify-center gap-2
            ${
													status === "uploading"
														? "bg-slate-700 text-slate-300 cursor-not-allowed"
														: "bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/25"
												}
          `}
				>
					{status === "uploading" ? (
						<>
							<Loader2 size={20} className="animate-spin" />
							Analyzing Resume...
						</>
					) : (
						"Upload your resume!"
					)}
				</button>
			)}

			{/* Success State */}
			{status === "success" && (
				<div className="mt-6 bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl flex flex-col items-center text-center animate-in fade-in slide-in-from-bottom-2">
					<div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-400 mb-3">
						<CheckCircle size={24} />
					</div>
					<h3 className="text-white font-semibold">Resume Uploaded!</h3>
					<p className="text-emerald-200/70 text-sm mt-1">
						We are currently scanning the Github repo for matches...
					</p>
				</div>
			)}
		</div>
	);
}
