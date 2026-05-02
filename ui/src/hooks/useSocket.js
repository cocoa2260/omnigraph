// React 19 + Socket.IO-client 연동[cite: 3]
import { io } from "socket.io-client";

const socket = io("http://3.34.45.173:8000");

socket.on("document_status", (data) => {
    // PDF Daol의 '진행 상태 UI 피드백' 기능 구현[cite: 3]
    toast.success(`${data.filename} 분석이 완료되었습니다!`);
    updateSummaryList(data.result);
});