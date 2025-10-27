// 百度贴吧主JavaScript文件

$(document).ready(function() {
    // 初始化工具提示
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // 初始化弹出框
    $('[data-bs-toggle="popover"]').popover();
    
    // 帖子点赞功能
    $('.like-btn').click(function() {
        var postId = $(this).data('post-id');
        var button = $(this);
        var likeCount = button.find('.like-count');
        
        // 显示加载状态
        var originalHtml = button.html();
        button.html('<div class="loading"></div>');
        button.prop('disabled', true);
        
        $.ajax({
            url: '/post/' + postId + '/like/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': getCSRFToken()
            },
            success: function(data) {
                likeCount.text(data.like_count);
                if (data.liked) {
                    button.removeClass('btn-outline-danger').addClass('btn-danger');
                } else {
                    button.removeClass('btn-danger').addClass('btn-outline-danger');
                }
                
                // 添加动画效果
                button.addClass('animate__animated animate__pulse');
                setTimeout(function() {
                    button.removeClass('animate__animated animate__pulse');
                }, 1000);
            },
            error: function(xhr, status, error) {
                console.error('点赞失败:', error);
                showAlert('点赞失败，请重试', 'danger');
            },
            complete: function() {
                button.html(originalHtml);
                button.prop('disabled', false);
            }
        });
    });
    
    // 评论点赞功能
    $('.like-comment-btn').click(function() {
        var commentId = $(this).data('comment-id');
        var button = $(this);
        var likeCount = button.find('.like-count');
        
        // 显示加载状态
        var originalHtml = button.html();
        button.html('<div class="loading"></div>');
        button.prop('disabled', true);
        
        $.ajax({
            url: '/comment/' + commentId + '/like/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': getCSRFToken()
            },
            success: function(data) {
                likeCount.text(data.like_count);
                if (data.liked) {
                    button.removeClass('btn-outline-danger').addClass('btn-danger');
                } else {
                    button.removeClass('btn-danger').addClass('btn-outline-danger');
                }
                
                // 添加动画效果
                button.addClass('animate__animated animate__pulse');
                setTimeout(function() {
                    button.removeClass('animate__animated animate__pulse');
                }, 1000);
            },
            error: function(xhr, status, error) {
                console.error('点赞失败:', error);
                showAlert('点赞失败，请重试', 'danger');
            },
            complete: function() {
                button.html(originalHtml);
                button.prop('disabled', false);
            }
        });
    });
    
    // 回复评论功能
    $('.reply-btn').click(function() {
        var commentId = $(this).data('comment-id');
        var commentElement = $('#comment-' + commentId);
        var replyForm = commentElement.find('.reply-form');
        
        if (replyForm.length === 0) {
            // 创建回复表单
            var formHtml = `
                <div class="reply-form mt-3">
                    <form class="reply-comment-form">
                        <input type="hidden" name="parent_id" value="${commentId}">
                        <div class="mb-2">
                            <textarea name="content" class="form-control" rows="2" placeholder="回复评论..." required></textarea>
                        </div>
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary btn-sm">回复</button>
                            <button type="button" class="btn btn-secondary btn-sm cancel-reply">取消</button>
                        </div>
                    </form>
                </div>
            `;
            
            commentElement.append(formHtml);
            
            // 绑定取消回复事件
            $('.cancel-reply').click(function() {
                $(this).closest('.reply-form').remove();
            });
            
            // 绑定回复表单提交事件
            $('.reply-comment-form').submit(function(e) {
                e.preventDefault();
                var form = $(this);
                var content = form.find('textarea[name="content"]').val();
                var parentId = form.find('input[name="parent_id"]').val();
                
                if (content.trim()) {
                    submitReply(form, content, parentId);
                }
            });
        }
    });
    
    // 搜索功能
    $('#search-form').submit(function(e) {
        e.preventDefault();
        var query = $(this).find('input[type="search"]').val().trim();
        
        if (query) {
            // 这里可以添加搜索功能
            console.log('搜索关键词:', query);
            showAlert('搜索功能开发中...', 'info');
        }
    });
    
    // 表单验证
    $('form').each(function() {
        var form = $(this);
        form.submit(function(e) {
            var requiredFields = form.find('[required]');
            var isValid = true;
            
            requiredFields.each(function() {
                var field = $(this);
                if (!field.val().trim()) {
                    field.addClass('is-invalid');
                    isValid = false;
                } else {
                    field.removeClass('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('请填写所有必填字段', 'warning');
            }
        });
    });
    
    // 自动隐藏消息提示
    $('.alert').not('.alert-permanent').delay(5000).fadeOut(300);
});

// 获取CSRF令牌
function getCSRFToken() {
    var csrfToken = $('meta[name="csrf-token"]').attr('content');
    if (!csrfToken) {
        csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    }
    return csrfToken;
}

// 显示消息提示
function showAlert(message, type) {
    var alertClass = 'alert-' + (type || 'info');
    var alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('main .container').prepend(alertHtml);
    
    // 自动隐藏
    setTimeout(function() {
        $('.alert').not('.alert-permanent').fadeOut(300, function() {
            $(this).remove();
        });
    }, 5000);
}

// 提交回复
function submitReply(form, content, parentId) {
    var postId = window.location.pathname.split('/')[2]; // 从URL获取帖子ID
    
    $.ajax({
        url: '/post/' + postId + '/comment/',
        type: 'POST',
        data: {
            'content': content,
            'parent_id': parentId,
            'csrfmiddlewaretoken': getCSRFToken()
        },
        success: function(data) {
            form.closest('.reply-form').remove();
            showAlert('回复成功', 'success');
            // 刷新页面或动态添加评论
            location.reload();
        },
        error: function(xhr, status, error) {
            console.error('回复失败:', error);
            showAlert('回复失败，请重试', 'danger');
        }
    });
}

// 图片预览功能
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#' + previewId).attr('src', e.target.result).show();
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// 字符计数
function countCharacters(textarea, counterId, maxLength) {
    var length = textarea.value.length;
    var counter = $('#' + counterId);
    counter.text(length + '/' + maxLength);
    
    if (length > maxLength) {
        counter.addClass('text-danger');
    } else {
        counter.removeClass('text-danger');
    }
}

// 滚动到指定元素
function scrollToElement(elementId, offset = 100) {
    var element = $('#' + elementId);
    if (element.length) {
        $('html, body').animate({
            scrollTop: element.offset().top - offset
        }, 500);
    }
}

// 复制到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('已复制到剪贴板', 'success');
    }, function(err) {
        console.error('复制失败:', err);
        showAlert('复制失败', 'danger');
    });
}

// 防抖函数
function debounce(func, wait) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    var inThrottle;
    return function() {
        var args = arguments;
        var context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(function() {
                inThrottle = false;
            }, limit);
        }
    };
}