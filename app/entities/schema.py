FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_company_info",
            "description": "Trả lời thông tin về công ty",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Câu hỏi cụ thể về công ty Fiine"
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_info",
            "description": "Trả lời về giá sản phẩm",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Tên gói sản phẩm cần hỏi (vd: PRO, VIP)"
                    }
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function":{
             "name": "get_technical_error_support",
            "description": "Hỗ trợ xử lý lỗi kỹ thuật thông qua AI assistant",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string", "description": "Mô tả vấn đề kỹ thuật cần hỗ trợ"}
                },
                "required": ["issue"]
            }
        }
    },
    {
        "type": "function",
        "function":{
             "name": "collect_technical_error_info",
            "description": "Thu thập thông tin lỗi kỹ thuật từ khách hàng và lưu vào database",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_message": {"type": "string", "description": "Tin nhắn từ người dùng chứa thông tin lỗi kỹ thuật (format: Họ tên: xxx, Tổ chức: xxx, Số điện thoại: xxx, Mô tả lỗi: xxx)"},
                    "name": {"type": "string", "description": "Họ tên khách hàng"},
                    "organization": {"type": "string", "description": "Tên tổ chức"},
                    "phone": {"type": "string", "description": "Số điện thoại liên hệ (bắt buộc nếu không có email)"},
                    "email": {"type": "string", "description": "Email người gửi (bắt buộc nếu không có số điện thoại)"},
                    "issue_description": {"type": "string", "description": "Mô tả lỗi chi tiết"},
                    "image_url": {"type": "string", "description": "URL hình ảnh lỗi (nếu có)", "nullable": True}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function":{
             "name": "process_technical_error_message",
            "description": "Xử lý tin nhắn lỗi kỹ thuật từ người dùng - tự động nhận diện và trích xuất thông tin",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_message": {"type": "string", "description": "Tin nhắn từ người dùng chứa thông tin lỗi kỹ thuật"}
                },
                "required": ["user_message"]
            }
        }
    },
    {
        "type": "function",
        "function":{
             "name": "auto_detect_and_process_technical_error",
            "description": "Tự động nhận diện và xử lý tin nhắn lỗi kỹ thuật từ người dùng - sử dụng khi người dùng gửi thông tin lỗi kỹ thuật",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_message": {"type": "string", "description": "Tin nhắn từ người dùng chứa thông tin lỗi kỹ thuật (format: Họ tên: xxx, Tổ chức: xxx, Số điện thoại: xxx, Mô tả lỗi: xxx)"}
                },
                "required": ["user_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_technical_error_with_confirmation",
            "description": "Xử lý thông tin lỗi kỹ thuật với xác nhận từ người dùng trước khi lưu vào database",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_message": {"type": "string", "description": "Tin nhắn từ người dùng chứa thông tin lỗi kỹ thuật hoặc phản hồi xác nhận"},
                    "conversation_state": {"type": "object", "description": "Trạng thái hội thoại (nếu có)"}
                },
                "required": ["user_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_total_price",
            "description": "Tính tổng chi phí dịch vụ dựa trên gói, số thành viên và số tháng.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "Tên gói dịch vụ: BASIC, PRO, VIP"
                    },
                    "members": {
                        "type": "integer",
                        "description": "Số lượng thành viên"
                    },
                    "months": {
                        "type": "integer",
                        "description": "Số tháng sử dụng"
                    }
                },
                "required": ["plan", "members", "months"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_register_steps",
            "description": "Lấy danh sách các bước đăng ký tài khoản Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_add_member_steps",
            "description": "Trả về các bước thêm thành viên theo nền tảng và phương thức. Nếu không có platform hoặc method, sẽ hỏi người dùng để làm rõ thông tin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["web", "mobile"],
                        "description": "Nền tảng người dùng sử dụng, ví dụ: 'web' hoặc 'mobile'"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["số điện thoại", "email", "link"],
                        "description": "Cách thêm thành viên: bằng số điện thoại, email, hoặc link"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_update_info_steps",
            "description": "Lấy danh sách các bước cập nhật thông tin cá nhân trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_create_work_steps",
            "description": "Lấy danh sách các bước tạo công việc mới trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_assign_work_steps",
            "description": "Lấy danh sách các bước giao việc cho thành viên trong tổ chức trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_list_work_steps",
            "description": "Lấy danh sách các bước xem công việc trong tổ chức trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_filter_work_steps",
            "description": "Lấy danh sách các bước lọc công việc trong tổ chức trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_update_detail_work_steps",
            "description": "Lấy danh sách các bước cập nhật chi tiết công việc trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_benefit_use_note",
            "description": "Lấy các lợi ích khi dùng Note trong Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_chat",
            "description": "Lấy các lợi ích khi dùng tính năng Chat trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }, 
    {
        "type": "function",
        "function": {
            "name": "get_use_checklist",
            "description": "Lấy cách sử dụng Checklist trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_create_field_steps",
            "description": "Lấy cách bước tạo Lĩnh vực trong Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_create_group_steps",
            "description": "Lấy cách bước tạo Nhóm trong Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_gantt_chart",
            "description": "Lấy cách bước tạo biểu đồ Gantt ",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_plan_working_day",
            "description": "Lên kế hoạch cho ngày làm việc",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_project_management",
            "description": "Quy trình quản lý dự án trên Fiine",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_share_work_with_link",
            "description": "Chia sẻ công việc thông qua link liên kết",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_share_work_snapshots",
            "description": "Chia sẻ công việc thông qua snapshots",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_task_management",
            "description": "Cách quản lý Task trên Fiine hiệu quả nhất",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_visitor_role",
            "description": "Vai trò của Visitor trong tổ chức",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_track_progress_task_i_assign",
            "description": "Theo dõi tiến độ công việc tôi giao",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_list_work_approval",
            "description": "Lấy ra danh sách công việc cần bạn phê duyệt",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_notice_update_work",
            "description": "Xem thông báo các cập nhập mới về công việc mà bạn tham gia",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_update_info_group",
            "description": "Cập nhập thông tin của nhóm",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_info_group",
            "description": "Xem thông tin về các nhóm có trong tổ chức",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_resource_group",
            "description": "Xem các tài nguyên của nhóm",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_create_work_group",
            "description": "Tạo mới công việc trong NHÓM",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_list_work_in_group",
            "description": "Xem danh sách công việc có trong nhóm",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_add_subfields",
            "description": "Tạo lĩnh vực/ dự án con trong lĩnh vực/ dự án cha",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_fields_management",
            "description": "Màn hình quản lý tất cả các lĩnh vực/ dự án của tổ chức",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_details_report_fields",
            "description": "Xem báo cáo của lĩnh vực/ tổ chức",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_work_process",
            "description": "Cách tạo và sử dụng tính năng quy trình công việc",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_reperat_work_periodically",
            "description": "Cách sử dụng tính năng lặp lại công việc theo định kỳ",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_accept_work",
            "description": "Cách sử dụng tính năng phê duyệt công việc",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_smart_schedule",
            "description": " Tạo yêu cầu nghỉ phép/xin đến trễ/xin về sớm/xin ra ngoài trong giờ làm việc",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
         "type": "function",
        "function": {
            "name": "get_smart_schedule_approval",
            "description": "Phê quyệt yêu cầu nghỉ phép/xin đến trễ/xin về sớm/xin ra ngoài trong giờ làm việc",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
