# --- 1. 加载所有需要的 R 包 ---
library(shiny)
library(readxl)
library(dplyr)
library(ggplot2)
library(plotly)
library(DT) # 用于交互式表格

# --- 2. 定义用户界面 (UI) ---
ui <- fluidPage(
  # 设置页面主题和标题
  theme = shinythemes::shinytheme("lumen"), # 使用一个清爽的主题
  titlePanel("销售数据仪表盘 (Sales Dashboard)"),
  
  # 侧边栏布局
  sidebarLayout(
    # -- 侧边栏：用于全局控制选项 --
    sidebarPanel(
      width = 3, # 侧边栏宽度
      h4("数据源选择"),
      
      # 下拉菜单 1: 选择 Excel 文件
      selectInput("file_select", "1. 选择 Excel 文件:", 
                  choices = NULL),
      
      # 下拉菜单 2: 选择工作表
      # 这个 UI 会根据文件选择动态生成
      uiOutput("sheet_selector_ui"),
      
      hr(), # 添加一条分割线
      
      h4("仪表盘说明"),
      p("请先选择一个数据文件和工作表，右侧的仪表盘将会自动更新。")
    ),
    
    # -- 主面板：用标签页展示不同功能 --
    mainPanel(
      width = 9, # 主面板宽度
      # 创建标签页布局
      tabsetPanel(
        id = "main_tabs",
        
        # 标签页 1: 关键指标概览
        tabPanel("关键指标概览", 
                 fluidRow(
                   # 使用 UIOutput 动态生成统计信息框
                   uiOutput("overview_boxes")
                 ),
                 hr(),
                 fluidRow(
                   h4("数据结构预览"),
                   # 显示数据结构的简要信息
                   verbatimTextOutput("data_structure")
                 )
        ),
        
        # 标签页 2: 数据浏览器
        tabPanel("数据浏览器", 
                 h4("浏览、搜索和排序数据"),
                 # 使用 DT::dataTableOutput 来显示强大的交互式表格
                 DT::dataTableOutput("interactive_table")
        ),
        
        # 标签页 3: 图表分析
        tabPanel("图表分析",
                 h4("自定义图表"),
                 fluidRow(
                   column(3, selectInput("plot_type", "选择图表类型:", 
                                         choices = c("散点图", "条形图", "直方图"))),
                   # 根据图表类型，动态显示不同的轴选择器
                   column(9, uiOutput("plot_axis_ui"))
                 ),
                 hr(),
                 plotlyOutput("dynamic_plot", height = "500px")
        )
      )
    )
  )
)

# --- 3. 定义服务器逻辑 (Server) ---
server <- function(input, output, session) {
  
  # --- 全局数据加载逻辑 (和之前类似) ---
  
  observe({
    excel_files <- list.files(path = "AI Master", pattern = "\\.xlsx?$", full.names = FALSE)
    updateSelectInput(session, "file_select", choices = excel_files)
  })
  
  selected_file_path <- reactive({
    req(input$file_select)
    file.path("AI Master", input$file_select)
  })
  
  selected_file_sheets <- eventReactive(selected_file_path(), {
    excel_sheets(path = selected_file_path())
  })
  
  output$sheet_selector_ui <- renderUI({
    req(selected_file_sheets())
    selectInput("sheet_select", "2. 选择工作表:", choices = selected_file_sheets())
  })
  
  selected_data <- reactive({
    req(selected_file_path(), input$sheet_select)
    read_excel(path = selected_file_path(), sheet = input$sheet_select)
  })
  
  # --- 标签页 1: 关键指标概览的逻辑 ---
  
  output$overview_boxes <- renderUI({
    df <- selected_data()
    req(df)
    
    total_rows <- nrow(df)
    total_cols <- ncol(df)
    
    # 查找数值类型的列用于计算
    numeric_cols <- df %>% select_if(is.numeric)
    
    # 创建统计信息框
    fluidRow(
      column(4, wellPanel(h5("总记录数"), h3(total_rows))),
      column(4, wellPanel(h5("总字段数 (列)"), h3(total_cols))),
      column(4, wellPanel(h5("数值型字段数"), h3(ncol(numeric_cols))))
    )
  })
  
  output$data_structure <- renderPrint({
    df <- selected_data()
    req(df)
    # 使用 str() 函数显示数据结构
    str(df)
  })
  
  # --- 标签页 2: 数据浏览器的逻辑 ---
  
  output$interactive_table <- DT::renderDataTable({
    df <- selected_data()
    req(df)
    DT::datatable(df, options = list(pageLength = 10, scrollX = TRUE), filter = 'top', extensions = 'Buttons',
                  rownames = FALSE)
  })
  
  # --- 标签页 3: 图表分析的逻辑 ---
  
  output$plot_axis_ui <- renderUI({
    df <- selected_data()
    req(df)
    col_names <- names(df)
    numeric_cols <- names(df)[sapply(df, is.numeric)]
    
    # 根据选择的图表类型显示不同的 UI
    if (input$plot_type == "散点图") {
      tagList(
        fluidRow(
          column(6, selectInput("scatter_x", "选择 X 轴:", choices = numeric_cols, selected = numeric_cols[1])),
          column(6, selectInput("scatter_y", "选择 Y 轴:", choices = numeric_cols, selected = numeric_cols[2]))
        )
      )
    } else if (input$plot_type == "条形图") {
      tagList(
        fluidRow(
          column(6, selectInput("bar_x", "选择类别 (X 轴):", choices = col_names)),
          column(6, selectInput("bar_y", "选择数值 (Y 轴, 可选):", choices = c("计数", numeric_cols)))
        )
      )
    } else if (input$plot_type == "直方图") {
      selectInput("hist_var", "选择数值变量:", choices = numeric_cols)
    }
  })
  
  output$dynamic_plot <- renderPlotly({
    df <- selected_data()
    req(df, input$plot_type)
    
    p <- NULL # 初始化图表
    
    if (input$plot_type == "散点图" && !is.null(input$scatter_x)) {
      p <- ggplot(df, aes_string(x = input$scatter_x, y = input$scatter_y)) + geom_point(alpha = 0.7)
    } else if (input$plot_type == "条形图" && !is.null(input$bar_x)) {
      if(input$bar_y == "计数"){
        p <- ggplot(df, aes_string(x = input$bar_x)) + geom_bar() + theme(axis.text.x = element_text(angle = 45, hjust = 1))
      } else {
        p <- ggplot(df, aes_string(x = input$bar_x, y = input$bar_y)) + geom_col() + theme(axis.text.x = element_text(angle = 45, hjust = 1))
      }
    } else if (input$plot_type == "直方图" && !is.null(input$hist_var)) {
      p <- ggplot(df, aes_string(x = input$hist_var)) + geom_histogram(bins = 30, fill="skyblue", alpha=0.8)
    }
    
    # 如果 p 被成功创建，就转换为 plotly 对象
    if (!is.null(p)) {
      ggplotly(p)
    }
  })
}

# --- 4. 运行 App ---
shinyApp(ui = ui, server = server)