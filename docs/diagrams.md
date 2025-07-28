# PAR MCP Inspector TUI - Architecture Diagrams

This document contains the architectural diagrams for the PAR MCP Inspector TUI project.

## Application Flow Diagram

Displays how CLI commands route to different parts of the application, from entry point through services to external MCP servers.

```mermaid
flowchart TD
    A[CLI Entry Point<br/>__main__.py] --> B{Command Type}

    B -->|tui| C[TUI Application<br/>MCPInspectorApp]
    B -->|connect| D[Direct STDIO Connection]
    B -->|connect-tcp| E[Direct HTTP+SSE Connection]
    B -->|debug| F[Debug Configured Server]
    B -->|servers| G[List Servers]
    B -->|download-resource| H[Download Resource<br/>CLI Command]
    B -->|roots-list| Z[List Filesystem Roots]
    B -->|roots-add| Y[Add Filesystem Root]
    B -->|roots-remove| X[Remove Filesystem Root]
    B -->|copy-config| W1[Copy Server Config<br/>Universal Format]
    B -->|copy-desktop| W2[Copy Desktop Config<br/>Claude Desktop]
    B -->|copy-code| W3[Copy Code Config<br/>Claude Code]

    C --> I[Server Manager<br/>Load Configuration]
    C --> J[MCP Service<br/>Connection Management]
    C --> K[TUI Widgets<br/>User Interface]

    H --> I
    H --> J
    H --> AA[File Type Detection<br/>Magic Numbers]
    H --> BB[File Download<br/>Auto-naming]

    Z --> I
    Y --> I  
    X --> I
    W1 --> I
    W2 --> I
    W3 --> I
    W1 --> CC[System Clipboard]
    W2 --> CC
    W3 --> CC

    I --> L[servers.yaml<br/>Configuration]

    J --> M{Transport Type}
    M -->|STDIO| N[StdioMCPClient]
    M -->|HTTP| O[HttpMCPClient]
    M -->|TCP| P[TcpMCPClient<br/>Legacy HTTP+SSE]

    N --> Q[MCP Server Process]
    O --> R[MCP HTTP Endpoint]
    P --> S[MCP HTTP+SSE Server]

    K --> T[Server Panel]
    K --> U[Resources View]
    K --> V[Tools View]
    K --> W[Prompts View]
    K --> ZZ[Roots View]
    K --> XX[Notifications View]
    K --> YY[Response Viewer]

    U --> AA
    U --> BB

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style F fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style G fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style H fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style I fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style J fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style M fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style N fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style O fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style P fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style Q fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style R fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style S fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style T fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style U fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style V fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style W fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style ZZ fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style XX fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style YY fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style X fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style Y fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style Z fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style AA fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style BB fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## TUI Component Architecture

Displays the layout structure of the TUI application with all panels and widgets.

```mermaid
flowchart TB
    subgraph "MCPInspectorApp"
        A[Header]
        B[Main Layout]
        C[Footer]
    end

    subgraph "Main Layout (Horizontal)"
        D[Left Panel<br/>Server Management]
        E[Center Panel<br/>Tabbed Content]
        F[Right Panel<br/>Notifications]
    end

    subgraph "Left Panel"
        G[Server Panel<br/>Server List & Controls]
        H[Connection Status<br/>Current State]
        AA[Server Config Dialog<br/>Add/Edit Servers]
    end

    subgraph "Center Panel (TabbedContent)"
        I[Resources Tab<br/>Browse & Read]
        J[Tools Tab<br/>Execute Tools]
        K[Prompts Tab<br/>Execute Prompts]
        NN[Roots Tab<br/>Manage Filesystem Roots]
        L[Notifications Tab<br/>Server Notifications]
    end

    subgraph "Right Panel"
        M[Response Viewer<br/>Formatted Output]
    end

    B --> D
    B --> E
    B --> F

    D --> G
    D --> H
    G --> AA

    E --> I
    E --> J
    E --> K
    E --> NN
    E --> L

    F --> M

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style F fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style G fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style H fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style I fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style J fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style NN fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style M fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## MCP Protocol Flow

Sequence diagram displaying the FastMCP-based communication flow between user, service, client, and MCP server with notification bridge.

```mermaid
sequenceDiagram
    participant U as User/TUI
    participant S as MCP Service
    participant C as MCP Client
    participant F as FastMCP Client
    participant N as NotificationBridge
    participant M as MCP Server

    U->>S: Connect to Server
    S->>C: Create Client (STDIO/TCP)
    C->>F: Initialize FastMCP Client
    F->>M: Initialize Connection
    M-->>F: Server Capabilities
    F-->>C: Connection Established
    C-->>S: Server Info & Capabilities
    S-->>U: Connection Status

    Note over U,M: Server Introspection via FastMCP

    U->>S: List Resources
    S->>C: list_resources()
    C->>F: client.list_resources()
    F->>M: JSON-RPC 2.0 Request
    M-->>F: Resources Response
    F-->>C: Parsed Resources List
    C-->>S: Resource Objects
    S-->>U: Update Resources View

    U->>S: List Tools
    S->>C: list_tools()
    C->>F: client.list_tools()
    F->>M: JSON-RPC 2.0 Request
    M-->>F: Tools Response
    F-->>C: Parsed Tools List
    C-->>S: Tool Objects
    S-->>U: Update Tools View

    U->>S: List Prompts
    S->>C: list_prompts()
    C->>F: client.list_prompts()
    F->>M: JSON-RPC 2.0 Request
    M-->>F: Prompts Response
    F-->>C: Parsed Prompts List
    C-->>S: Prompt Objects
    S-->>U: Update Prompts View

    Note over U,M: Roots Management via MCP Client

    U->>S: Get Roots
    S->>C: get_roots()
    C-->>S: Current Roots List
    S-->>U: Update Roots View

    U->>S: Add Root
    S->>C: add_root(uri)
    C-->>S: Root Added
    S-->>U: Refresh Roots Display

    U->>S: Remove Root
    S->>C: remove_root(uri)
    C-->>S: Root Removed
    S-->>U: Refresh Roots Display

    Note over U,M: Tool Execution via FastMCP

    U->>S: Execute Tool
    S->>C: call_tool(name, args)
    C->>F: client.call_tool(name, args)
    F->>M: JSON-RPC 2.0 Request
    M-->>F: Tool Result
    F-->>C: CallToolResult Object
    C-->>S: Parsed Result
    S-->>U: Display Response

    Note over U,M: FastMCP Notifications with Bridge

    M->>F: ServerNotification
    F->>N: MessageHandler.on_notification()
    N->>N: Convert to MCPNotification
    N->>C: _handle_notification()
    C->>S: Process Notification
    S->>S: Parse Notification Type
    S->>U: Add to Notifications Tab
    S->>U: Show Toast Notification

    alt List Changed Notification
        S->>S: _handle_list_changed_notification()
        S->>U: Auto-refresh Relevant View
        S->>U: Show Refresh Success
    else Message Notification
        Note over S,U: Display message only, no refresh
    end
```

## Client Transport Architecture

Displays the transport types (STDIO/HTTP/TCP) using FastMCP's transport layer with notification bridge architecture.

```mermaid
flowchart TD
    A[MCP Service] --> B{Transport Type}

    B -->|stdio| C[StdioMCPClient]
    B -->|http| D[HttpMCPClient]
    B -->|tcp| E[TcpMCPClient<br/>Legacy HTTP+SSE]

    subgraph "STDIO Transport with FastMCP (Recommended)"
        C --> C1[FastMCP Client]
        C1 --> C2[StdioTransport]
        C2 --> C3[Process Spawning]
        C3 --> C4[stdin/stdout pipes]
        C4 --> C5[MCP Server Process]

        C1 --> C6[NotificationBridge]
        C6 --> C7[MessageHandler System]
        C7 --> C8[Custom Notification Handlers]
    end

    subgraph "HTTP Transport with FastMCP"
        D --> D1[FastMCP Client]
        D1 --> D2[StreamableHttpTransport]
        D2 --> D3[HTTP/HTTPS Connection]
        D3 --> D4[MCP HTTP Endpoint]

        D1 --> D6[Direct MessageHandler]
        D6 --> D7[Custom Notification Handlers]
    end

    subgraph "TCP Transport with FastMCP (Legacy)"
        E --> E1[FastMCP Client]
        E1 --> E2[SSETransport]
        E2 --> E3[HTTP+SSE Connection]
        E3 --> E4[MCP HTTP Server]

        E1 --> E6[Direct MessageHandler]
        E6 --> E7[Custom Notification Handlers]
    end

    subgraph "FastMCP Protocol Layer"
        K[JSON-RPC 2.0 Messages]
        L[Automatic Serialization]
        M[Built-in Error Handling]
        N[Capability Negotiation]
        O[Real-time Notifications]
    end

    C1 --> K
    D1 --> K
    E1 --> K
    K --> L
    L --> M
    M --> N
    N --> O

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C1 fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C2 fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C3 fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C4 fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C5 fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C6 fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C7 fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C8 fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D1 fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D2 fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D3 fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D4 fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D6 fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D7 fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E1 fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E2 fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E3 fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E4 fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E6 fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E7 fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style M fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style N fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style O fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Data Flow Through Layers

Displays how data flows between the presentation, service, client, and external layers.

```mermaid
flowchart LR
    subgraph "Presentation Layer"
        A[TUI Widgets]
        B[User Input]
        C[Response Display]
    end

    subgraph "Service Layer"
        D[MCP Service]
        E[Server Manager]
        F[Configuration]
    end

    subgraph "Client Layer"
        G[MCP Clients]
        H[Transport Logic]
        I[Protocol Handler]
    end

    subgraph "External"
        J[MCP Servers]
        K[Configuration Files]
    end

    B --> A
    A --> D
    D --> E
    E --> F
    F --> K

    D --> G
    G --> H
    H --> I
    I --> J

    J --> I
    I --> H
    H --> G
    G --> D
    D --> A
    A --> C

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style F fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style G fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style H fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style I fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style J fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#581c87,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Color Legend

The diagrams use a consistent color scheme optimized for dark mode:

- **Navy Blue** (`#1e3a8a`) - Primary application components
- **Green** (`#059669`) - Main flow and success states  
- **Red** (`#dc2626`) - CLI commands and critical paths
- **Purple** (`#7c3aed`) - Decision points and branching logic
- **Orange** (`#ea580c`) - Transport and communication layers
- **Cyan** (`#0891b2`) - UI components and widgets
- **Gray** (`#374151`) - External systems and files
- **Dark Red** (`#991b1b`) - External servers
- **Dark Purple** (`#581c87`) - Configuration files

All elements feature white text (`#ffffff`) and white borders for maximum contrast and readability in both light and dark mode environments.

## Form Validation Flow

Displays the reactive form validation system that controls execute button states in Tools and Prompts views.

```mermaid
sequenceDiagram
    participant U as User
    participant TV as Tools/Prompts View
    participant DF as DynamicForm
    participant FB as Form Field
    participant EB as Execute Button

    Note over U,EB: Tool/Prompt Selection

    U->>TV: Select Tool/Prompt
    TV->>DF: Create Form with Fields
    DF->>FB: Mount Input Fields
    FB-->>DF: Fields Ready
    DF->>DF: on_mount() - Post-mount Validation
    DF->>DF: Initial Validation Check (Race-safe)
    DF->>TV: ValidationChanged(is_valid)
    TV->>EB: Update Button State

    Note over U,EB: User Interaction & Validation

    U->>FB: Type in Required Field
    FB->>DF: on_input_changed()
    DF->>DF: _check_validation_state()
    DF->>DF: validate() - Check All Required Fields

    alt All Required Fields Filled
        DF->>TV: ValidationChanged(true)
        TV->>EB: Enable Execute Button
        EB-->>U: Button Available
    else Required Fields Missing
        DF->>TV: ValidationChanged(false)
        TV->>EB: Disable Execute Button
        EB-->>U: Button Disabled
    end

    Note over U,EB: Array Field Handling

    U->>FB: Add/Remove Array Item
    FB->>DF: _notify_parent_change()
    DF->>DF: _check_validation_state()
    DF->>TV: ValidationChanged(is_valid)
    TV->>EB: Update Button State

    Note over U,EB: Execute Action

    U->>EB: Click Execute (if enabled)
    EB->>TV: Execute Tool/Prompt
    TV->>DF: get_values()
    DF-->>TV: Form Data
    TV->>TV: Call MCP Service
```

## Dynamic Form Architecture

Displays the structure and relationships within the form validation system.

```mermaid
flowchart TD
    subgraph "Form Validation System"
        A[DynamicForm Widget]
        B[ValidationChanged Message]
        C[Form Fields Collection]
    end

    subgraph "Field Types"
        D[Input Fields<br/>Text/Number]
        E[Select Fields<br/>Dropdown]
        F[Checkbox Fields<br/>Boolean]
        G[ArrayField Widget<br/>Dynamic List]
    end

    subgraph "Validation Logic"
        H[validate() Method<br/>Check Required Fields]
        I[is_valid() Method<br/>No Errors Check]
        J[_check_validation_state()<br/>State Change Detection]
    end

    subgraph "Event Handling"
        K[on_input_changed()]
        L[on_select_changed()]
        M[on_checkbox_changed()]
        N[Array Item Changes]
    end

    subgraph "Parent Views"
        O[ToolsView<br/>Execute Tool Button]
        P[PromptsView<br/>Execute Prompt Button]
    end

    A --> C
    C --> D
    C --> E
    C --> F
    C --> G

    D --> K
    E --> L
    F --> M
    G --> N

    K --> J
    L --> J
    M --> J
    N --> J

    J --> H
    H --> I
    I --> B

    B --> O
    B --> P

    O --> Q[Button State Update]
    P --> Q

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style F fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style G fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style H fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style I fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style J fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style M fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style N fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style O fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style P fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style Q fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## File Type Detection Flow

Displays the enhanced file type detection system using magic numbers for proper file extensions and MIME type handling.

```mermaid
flowchart TD
    A[Resource Response<br/>from MCP Server] --> B{Content Type}

    B -->|blob| C[Base64 Binary Data]
    B -->|text| D[Text Data]

    C --> E[Decode Base64]
    E --> F{MIME Type Check}

    F -->|Specific MIME| G[Use MIME Extension<br/>e.g., image/png → .png]
    F -->|Generic MIME<br/>octet-stream| H[Magic Number Detection<br/>filetype.guess()]

    H --> I{Magic Detected?}
    I -->|Yes| J[Use Detected Extension<br/>e.g., PDF magic → .pdf]
    I -->|No| K[Check Resource Name<br/>for Extension]

    D --> L{Text MIME Type}
    L -->|Specific MIME| G
    L -->|Generic MIME| M[Encode as UTF-8<br/>for Magic Check]
    M --> H

    K --> N{Extension Found?}
    N -->|Yes| O[Use Name Extension]
    N -->|No| P[Default Extension<br/>.bin for binary, .txt for text]

    G --> Q[Generate Safe Filename]
    J --> Q
    O --> Q
    P --> Q

    Q --> R[Create File Path]
    R --> S[Save to Disk]
    S --> T[File Saved Successfully]

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style F fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style G fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style H fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style I fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style J fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style M fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style N fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style O fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style P fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style Q fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style R fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style S fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style T fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Server Notifications Architecture

Displays the FastMCP-based real-time notification system with NotificationBridge for protocol adaptation.

```mermaid
flowchart TD
    subgraph "MCP Server"
        A[Server Events<br/>Tools/Resources/Prompts Changes]
        B[Message Generation<br/>Info/Warning/Error]
        C[Notification Sender]
    end

    subgraph "Client Capabilities"
        D[Client Declares Capabilities<br/>tools.listChanged: true<br/>resources.listChanged: true<br/>prompts.listChanged: true]
    end

    subgraph "FastMCP Transport Layer"
        E[JSON-RPC 2.0 Notification<br/>ServerNotification Type]
        F[StdioTransport/WSTransport]
        G[FastMCP Client]
    end

    subgraph "Notification Bridge (STDIO Only)"
        H[NotificationBridge Class<br/>extends MessageHandler]
        I[on_notification() Method<br/>Protocol Conversion]
        J[Convert to MCPNotification<br/>Extract params & method]
    end

    subgraph "MCP Client Layer"
        K[Base Client Handler<br/>_handle_notification()]
        L[Notification Routing<br/>by Method Type]
    end

    subgraph "MCP Service"
        M[Notification Processing<br/>_handle_mcp_notification()]
        N[ServerNotification Model<br/>With Server Context]
        O[Callback System]
    end

    subgraph "TUI Application"
        P[Notification Panel<br/>Display with Server Context]
        Q[Auto-refresh Logic<br/>list_changed notifications]
        R[Toast Control Logic<br/>Per-server + Tab-aware]
        S[Toast Notifications<br/>System alerts]
    end

    subgraph "UI Updates"
        T[Tools View Refresh]
        U[Resources View Refresh]
        V[Prompts View Refresh]
        W[Notification History]
    end

    A --> C
    B --> C
    C --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    O --> P
    O --> Q
    O --> R
    R --> S

    Q --> T
    Q --> U
    Q --> V
    P --> W

    D -.->|Enables| C

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style F fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style G fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style H fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style I fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style J fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style M fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style N fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style O fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style P fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style Q fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style R fill:#581c87,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style S fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style T fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style U fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style V fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style W fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Server Configuration Dialog Flow

Displays the server configuration dialog workflow including toast notification controls.

```mermaid
flowchart TD
    A[User Clicks Add/Edit Server] --> B{Dialog Mode}

    B -->|Add Mode| C[ServerConfigDialog<br/>mode="add"]
    B -->|Edit Mode| D[ServerConfigDialog<br/>server=existing<br/>mode="edit"]

    C --> E[Initialize Form<br/>Default Values]
    D --> F[Initialize Form<br/>Existing Values]

    E --> G[Server Configuration Form]
    F --> G

    subgraph "Server Configuration Form"
        H[Server Name Input]
        I[Transport Type<br/>STDIO/TCP Radio]
        J[STDIO Config<br/>Command, Args, Env]
        K[TCP Config<br/>Host, Port]
        L[Toast Notifications<br/>Checkbox]
    end

    G --> H
    G --> I
    G --> J
    G --> K
    G --> L

    I --> M{Transport Selected}
    M -->|STDIO| N[Show STDIO Config]
    M -->|TCP| O[Show TCP Config]

    L --> P[Toast Setting<br/>Default: true]

    H --> Q[Form Validation]
    N --> Q
    O --> Q
    P --> Q

    Q --> R{Valid?}
    R -->|No| S[Show Error Message]
    R -->|Yes| T[Create MCPServer Object]

    S --> G
    T --> U[Include toast_notifications<br/>from Checkbox]

    U --> V{Dialog Result}
    V -->|Save| W[Return Server Object]
    V -->|Cancel| X[Return None]

    W --> Y[Server Panel Handler]
    X --> Z[No Action]

    Y --> AA{Operation Type}
    AA -->|Add| BB[server_manager.add_server()]
    AA -->|Edit| CC[server_manager.update_server()]

    BB --> DD[Update selected_server<br/>Reference]
    CC --> DD

    DD --> EE[_refresh_server_list()]
    EE --> FF[Maintain Selection State]
    FF --> GG[Server List Updated<br/>Toast Setting Active]

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style P fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style U fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style DD fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style FF fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style GG fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
```

## Notification Types Flow

Displays the different types of notifications and their handling paths through the system.

```mermaid
flowchart TD
    A[Server Notification Received] --> B{Notification Type}

    B -->|notifications/tools/list_changed| C[Tools List Changed]
    B -->|notifications/resources/list_changed| D[Resources List Changed]
    B -->|notifications/prompts/list_changed| E[Prompts List Changed]
    B -->|notifications/message| F[Server Message]
    B -->|other| G[Generic Notification]

    C --> H[Auto-refresh Tools View]
    D --> I[Auto-refresh Resources View]
    E --> J[Auto-refresh Prompts View]
    F --> K[Extract Level & Data<br/>Format: [LEVEL] message]
    G --> L[Generic Message Format]

    H --> M[Show Refresh Success Notification]
    I --> M
    J --> M
    K --> N[Display Formatted Message]
    L --> N

    M --> O[Add to Notifications Tab]
    N --> O

    O --> P[Show Toast Notification]
    P --> Q[Update Notification Count]
    Q --> R[Scroll to Top (newest first)]

    style A fill:#1e3a8a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style B fill:#7c3aed,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style C fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style D fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style E fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style F fill:#ea580c,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style G fill:#374151,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style H fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style I fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style J fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style K fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style L fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style M fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style N fill:#0369a1,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style O fill:#991b1b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style P fill:#581c87,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style Q fill:#581c87,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style R fill:#581c87,stroke:#ffffff,stroke-width:2px,color:#ffffff
```
