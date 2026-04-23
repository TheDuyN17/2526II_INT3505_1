#!/bin/bash
# =============================================================================
# Script chạy Newman tự động - API Testing Buổi 8
# Sử dụng: bash run_tests.sh
# =============================================================================

set -e

# --- Định nghĩa màu sắc output ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COLLECTION="product_api_tests.json"
REPORTS_DIR="reports"
ITERATIONS=10

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   API TESTING - JSONPlaceholder        ${NC}"
echo -e "${BLUE}   Iterations: ${ITERATIONS}                      ${NC}"
echo -e "${BLUE}========================================${NC}"

# --- Bước 1: Kiểm tra Newman đã cài chưa ---
echo -e "\n${YELLOW}[1/4] Kiểm tra Newman...${NC}"
if ! command -v newman &>/dev/null; then
    echo -e "${RED}[LỖI] Newman chưa được cài đặt!${NC}"
    echo -e "${YELLOW}Cài đặt bằng lệnh:${NC}"
    echo "  npm install -g newman"
    echo "  npm install -g newman-reporter-htmlextra"
    exit 1
fi
echo -e "${GREEN}[OK] Newman: $(newman --version)${NC}"

# --- Bước 2: Kiểm tra htmlextra reporter ---
echo -e "\n${YELLOW}[2/4] Kiểm tra htmlextra reporter...${NC}"
HTMLEXTRA_OK=false
if npm list -g newman-reporter-htmlextra &>/dev/null 2>&1; then
    HTMLEXTRA_OK=true
    echo -e "${GREEN}[OK] newman-reporter-htmlextra đã cài${NC}"
else
    echo -e "${YELLOW}[WARN] newman-reporter-htmlextra chưa cài, sẽ dùng reporter mặc định${NC}"
    echo -e "       Cài bằng: npm install -g newman-reporter-htmlextra"
fi

# --- Bước 3: Kiểm tra file collection tồn tại ---
if [ ! -f "$COLLECTION" ]; then
    echo -e "${RED}[LỖI] Không tìm thấy: $COLLECTION${NC}"
    exit 1
fi

# --- Bước 4: Tạo thư mục reports nếu chưa có ---
echo -e "\n${YELLOW}[3/4] Chuẩn bị thư mục reports...${NC}"
mkdir -p "$REPORTS_DIR"
echo -e "${GREEN}[OK] Thư mục $REPORTS_DIR/ sẵn sàng${NC}"

# --- Bước 5: Chạy Newman ---
echo -e "\n${YELLOW}[4/4] Chạy Newman ($ITERATIONS iterations)...${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

# Bỏ set -e tạm thời để bắt exit code của Newman
set +e

if [ "$HTMLEXTRA_OK" = true ]; then
    # Chạy với htmlextra reporter (đẹp hơn)
    newman run "$COLLECTION" \
        --iteration-count "$ITERATIONS" \
        --timeout-request 10000 \
        --reporters cli,htmlextra,json \
        --reporter-htmlextra-export "$REPORTS_DIR/report.html" \
        --reporter-htmlextra-title "JSONPlaceholder API Test Report" \
        --reporter-json-export "$REPORTS_DIR/report.json"
else
    # Fallback: CLI + JSON
    newman run "$COLLECTION" \
        --iteration-count "$ITERATIONS" \
        --timeout-request 10000 \
        --reporters cli,json \
        --reporter-json-export "$REPORTS_DIR/report.json"
fi

NEWMAN_EXIT=$?
set -e

# --- Tóm tắt kết quả ---
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "\n${YELLOW}=== TÓM TẮT KẾT QUẢ ===${NC}"

if [ -f "$REPORTS_DIR/report.json" ]; then
    # Dùng python để parse JSON report
    if command -v python3 &>/dev/null; then
        python3 - "$REPORTS_DIR/report.json" << 'EOF'
import json, sys
try:
    data = json.load(open(sys.argv[1]))
    s = data['run']['stats']
    t = data['run']['timings']
    total = s['assertions']['total']
    failed = s['assertions']['failed']
    passed = total - failed
    avg = t.get('responseAverage', 0)
    print(f"  Tổng assertions : {total}")
    print(f"  Passed          : {passed}")
    print(f"  Failed          : {failed}")
    print(f"  Error rate      : {failed/total*100:.1f}%" if total else "  Error rate : N/A")
    print(f"  Avg response    : {avg:.0f} ms")
except Exception as e:
    print(f"  (Không đọc được report: {e})")
EOF
    fi
fi

# In vị trí file report
if [ -f "$REPORTS_DIR/report.html" ]; then
    echo -e "\n${GREEN}HTML Report: $REPORTS_DIR/report.html${NC}"
fi
echo -e "${GREEN}JSON Report: $REPORTS_DIR/report.json${NC}"

# Kết thúc với exit code của Newman
if [ $NEWMAN_EXIT -eq 0 ]; then
    echo -e "\n${GREEN}✓ TẤT CẢ TESTS ĐÃ PASS!${NC}"
else
    echo -e "\n${RED}✗ CÓ TESTS BỊ FAIL! Xem report để biết chi tiết.${NC}"
fi

exit $NEWMAN_EXIT
