import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle } from 'lucide-react'

export default function FileUpload({ onFileSelect, isUploading, error }) {
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            onFileSelect(acceptedFiles[0])
        }
    }, [onFileSelect])

    const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf']
        },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024, // 10MB
        disabled: isUploading
    })

    return (
        <div>
            <div
                {...getRootProps()}
                className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-primary bg-orange-50 scale-105' : 'border-gray-300 hover:border-primary'}
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
            >
                <input {...getInputProps()} />

                <div className="flex flex-col items-center space-y-4">
                    {isUploading ? (
                        <>
                            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
                            <p className="text-lg font-semibold text-gray-700">
                                Processing your document...
                            </p>
                            <p className="text-sm text-gray-500 tamil-text">
                                உங்கள் ஆவணத்தை செயலாக்குகிறோம்...
                            </p>
                        </>
                    ) : isDragActive ? (
                        <>
                            <Upload className="w-16 h-16 text-primary" />
                            <p className="text-lg font-semibold text-gray-700">
                                Drop your PDF here
                            </p>
                            <p className="text-sm text-gray-500 tamil-text">
                                PDF ஐ இங்கே விடவும்
                            </p>
                        </>
                    ) : (
                        <>
                            <FileText className="w-16 h-16 text-gray-400" />
                            <div>
                                <p className="text-lg font-semibold text-gray-700 mb-2">
                                    📁 Drag & Drop PDF Here
                                </p>
                                <p className="text-sm text-gray-500 mb-1">or</p>
                                <button className="btn-primary">
                                    Browse Files
                                </button>
                            </div>
                            <div className="text-sm text-gray-500 space-y-1">
                                <p>Supported: PDF only</p>
                                <p>Max size: 10MB | Max pages: 30</p>
                                <p className="tamil-text">PDF மட்டும் • அதிகபட்சம்: 10MB</p>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="text-sm font-semibold text-red-800">Upload Failed</p>
                        <p className="text-sm text-red-600">{error}</p>
                    </div>
                </div>
            )}

            {/* File Rejection Errors */}
            {fileRejections.length > 0 && (
                <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm font-semibold text-yellow-800 mb-2">File not accepted:</p>
                    {fileRejections.map(({ file, errors }) => (
                        <div key={file.path} className="text-sm text-yellow-700">
                            {errors.map(e => (
                                <p key={e.code}>• {e.message}</p>
                            ))}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
