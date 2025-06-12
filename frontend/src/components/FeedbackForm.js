import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Send, 
  Image as ImageIcon, 
  FileText, 
  X, 
  Upload,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const FeedbackForm = ({ onSubmit, isDisabled, isSubmitted }) => {
  const [text, setText] = useState('');
  const [images, setImages] = useState([]);
  const [files, setFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 图片拖拽上传
  const {
    getRootProps: getImageRootProps,
    getInputProps: getImageInputProps,
    isDragActive: isImageDragActive
  } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp', '.svg']
    },
    onDrop: (acceptedFiles) => {
      const newImages = acceptedFiles.map(file => ({
        file,
        name: file.name,
        size: file.size,
        url: URL.createObjectURL(file),
        id: Math.random().toString(36).substr(2, 9)
      }));
      setImages(prev => [...prev, ...newImages]);
    },
    disabled: isDisabled
  });

  // 文件拖拽上传
  const {
    getRootProps: getFileRootProps,
    getInputProps: getFileInputProps,
    isDragActive: isFileDragActive
  } = useDropzone({
    accept: {
      'application/*': [],
      'text/*': [],
      'audio/*': [],
      'video/*': []
    },
    onDrop: (acceptedFiles) => {
      const newFiles = acceptedFiles.map(file => ({
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        id: Math.random().toString(36).substr(2, 9)
      }));
      setFiles(prev => [...prev, ...newFiles]);
    },
    disabled: isDisabled
  });

  const removeImage = (id) => {
    setImages(prev => {
      const updated = prev.filter(img => img.id !== id);
      // 清理 URL
      const removed = prev.find(img => img.id === id);
      if (removed) {
        URL.revokeObjectURL(removed.url);
      }
      return updated;
    });
  };

  const removeFile = (id) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim() && images.length === 0 && files.length === 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      // 准备提交数据
      const feedbackData = {
        text: text.trim(),
        images: images.map(img => ({
          name: img.name,
          size: img.size,
          url: img.url
        })),
        files: files.map(file => ({
          name: file.name,
          size: file.size,
          type: file.type
        }))
      };

      await onSubmit(feedbackData);
      
      // 清空表单
      setText('');
      setImages([]);
      setFiles([]);
      
    } catch (error) {
      console.error('提交反馈失败:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isSubmitted) {
    return (
      <div className="glass-effect rounded-2xl p-6 card-shadow">
        <div className="text-center text-white">
          <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400" />
          <h3 className="text-lg font-semibold mb-2">反馈已提交</h3>
          <p className="text-white/80">感谢您的反馈！会话已完成。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-effect rounded-2xl p-6 card-shadow">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Send className="w-5 h-5 mr-2" />
        提交反馈
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 文本输入 */}
        <div>
          <label className="block text-white/90 text-sm font-medium mb-2">
            📝 您的反馈
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="请输入您的反馈、建议或回答...&#10;&#10;支持 Markdown 格式：&#10;- **粗体文本**&#10;- *斜体文本*&#10;- `代码片段`&#10;- [链接](URL)"
            className="input-field h-32 resize-none"
            disabled={isDisabled}
          />
        </div>

        {/* 图片上传 */}
        <div>
          <label className="block text-white/90 text-sm font-medium mb-2">
            🖼️ 图片上传
          </label>
          <div
            {...getImageRootProps()}
            className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
              isImageDragActive
                ? 'border-blue-400 bg-blue-50/10'
                : 'border-white/30 hover:border-white/50'
            } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getImageInputProps()} />
            <ImageIcon className="w-8 h-8 mx-auto mb-2 text-white/60" />
            <p className="text-white/80 text-sm">
              {isImageDragActive ? '释放以上传图片' : '点击或拖拽上传图片'}
            </p>
          </div>
          
          {/* 图片预览 */}
          {images.length > 0 && (
            <div className="mt-3 grid grid-cols-2 gap-2">
              {images.map((image) => (
                <div key={image.id} className="relative group">
                  <img
                    src={image.url}
                    alt={image.name}
                    className="w-full h-20 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => removeImage(image.id)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                  <div className="absolute bottom-1 left-1 bg-black/50 text-white text-xs px-1 rounded">
                    {formatFileSize(image.size)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 文件上传 */}
        <div>
          <label className="block text-white/90 text-sm font-medium mb-2">
            📎 文件上传
          </label>
          <div
            {...getFileRootProps()}
            className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
              isFileDragActive
                ? 'border-purple-400 bg-purple-50/10'
                : 'border-white/30 hover:border-white/50'
            } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getFileInputProps()} />
            <Upload className="w-8 h-8 mx-auto mb-2 text-white/60" />
            <p className="text-white/80 text-sm">
              {isFileDragActive ? '释放以上传文件' : '点击或拖拽上传文件'}
            </p>
          </div>
          
          {/* 文件列表 */}
          {files.length > 0 && (
            <div className="mt-3 space-y-2">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between bg-white/10 rounded-lg p-2"
                >
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-white/60" />
                    <div>
                      <p className="text-white text-sm">{file.name}</p>
                      <p className="text-white/60 text-xs">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(file.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 提交按钮 */}
        <button
          type="submit"
          disabled={isDisabled || isSubmitting || (!text.trim() && images.length === 0 && files.length === 0)}
          className="btn-primary w-full flex items-center justify-center space-x-2"
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>提交中...</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>提交反馈</span>
            </>
          )}
        </button>

        {/* 状态提示 */}
        {isDisabled && !isSubmitted && (
          <div className="flex items-center space-x-2 text-yellow-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            <span>等待连接到服务器...</span>
          </div>
        )}
      </form>
    </div>
  );
};

export default FeedbackForm;
