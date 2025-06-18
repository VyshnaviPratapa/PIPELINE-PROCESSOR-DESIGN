module PipelineProcessor (
    input clk, reset
);

// Define registers
reg [15:0] instr_mem [0:15];  // Instruction memory
reg [7:0] data_mem [0:255];   // Data memory
reg [7:0] reg_file [0:7];     // Register file

// Pipeline registers
reg [15:0] IF_ID, ID_EX;
reg [15:0] EX_MEM;
reg [2:0]  EX_MEM_dest;
reg [7:0]  EX_MEM_val;
reg        MEM_WB_write;
reg [2:0]  MEM_WB_dest;
reg [7:0]  MEM_WB_val;

// Fetch program counter
reg [3:0] pc;

// Opcode encoding
localparam ADD = 4'b0000,
           SUB = 4'b0001,
           LOAD = 4'b0010;

// Instruction fetch
always @(posedge clk or posedge reset) begin
    if (reset) begin
        pc <= 0;
        IF_ID <= 0;
    end else begin
        IF_ID <= instr_mem[pc];
        pc <= pc + 1;
    end
end

// Decode + Register Fetch
reg [3:0] opcode;
reg [2:0] rd, rs1, rs2;
reg [7:0] reg1_val, reg2_val;
always @(posedge clk) begin
    opcode <= IF_ID[15:12];
    rd <= IF_ID[11:9];
    rs1 <= IF_ID[8:6];
    rs2 <= IF_ID[5:3];
    reg1_val <= reg_file[IF_ID[8:6]];
    reg2_val <= reg_file[IF_ID[5:3]];
    ID_EX <= IF_ID;
end

// Execute stage
always @(posedge clk) begin
    case (opcode)
        ADD: begin
            EX_MEM_val <= reg1_val + reg2_val;
            EX_MEM_dest <= rd;
            MEM_WB_write <= 1;
        end
        SUB: begin
            EX_MEM_val <= reg1_val - reg2_val;
            EX_MEM_dest <= rd;
            MEM_WB_write <= 1;
        end
        LOAD: begin
            EX_MEM_val <= data_mem[reg1_val + IF_ID[5:0]]; // Offset
            EX_MEM_dest <= rd;
            MEM_WB_write <= 1;
        end
    endcase
end

// Write Back
always @(posedge clk) begin
    if (MEM_WB_write) begin
        reg_file[EX_MEM_dest] <= EX_MEM_val;
    end
end

endmodule
//TEST BENCH
initial begin
    reset = 1; clk = 0;
    #5 reset = 0;
    
    // Sample instructions
    instr_mem[0] = 16'b0000_001_010_011_0000;  // ADD R1, R2, R3
    instr_mem[1] = 16'b0001_100_101_110_0000;  // SUB R4, R5, R6
    instr_mem[2] = 16'b0010_111_000_00000100;  // LOAD R7, 4(R0)
    
    // Sample data
    reg_file[2] = 8'd10;
    reg_file[3] = 8'd20;
    data_mem[4] = 8'd99;

    // Simulate clock
    forever #5 clk = ~clk;
end
