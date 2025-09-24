import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, scrolledtext
import subprocess
import threading
import requests
import json

class IPFSClusterFullApp:
    def __init__(self, master):
        self.master = master
        self.master.title("IPFS & IPFS Cluster 全功能控制面板")
        self.master.geometry("800x700")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.ipfs_proc = None
        self.cluster_proc = None

        self.ipfs_api_url = "http://127.0.0.1:5001/api/v0"
        self.cluster_api_url = "http://127.0.0.1:9094/"

        # 建立 UI
        self.create_widgets()

    def log(self, msg):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, msg + "\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)

    def create_widgets(self):
        # 啟動/停止服務按鈕區
        frame1 = tk.Frame(self.master)
        frame1.pack(pady=5, fill=tk.X)

        tk.Button(frame1, text="啟動 IPFS", command=self.start_ipfs).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="啟動 IPFS Cluster", command=self.start_cluster).pack(side=tk.LEFT, padx=5)
        tk.Button(frame1, text="停止所有服務", command=self.stop_all).pack(side=tk.LEFT, padx=5)

        # IPFS 功能按鈕區
        frame_ipfs = tk.LabelFrame(self.master, text="IPFS 功能")
        frame_ipfs.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(frame_ipfs, text="加入檔案 (add)", command=self.ipfs_add).grid(row=0, column=0, padx=3, pady=3)
        tk.Button(frame_ipfs, text="取得檔案內容 (cat)", command=self.ipfs_cat).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(frame_ipfs, text="列出目錄 (ls)", command=self.ipfs_ls).grid(row=0, column=2, padx=3, pady=3)

        tk.Button(frame_ipfs, text="Pin 新增 (pin/add)", command=self.ipfs_pin_add).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(frame_ipfs, text="Pin 移除 (pin/rm)", command=self.ipfs_pin_rm).grid(row=1, column=1, padx=3, pady=3)
        tk.Button(frame_ipfs, text="列出 Pin (pin/ls)", command=self.ipfs_pin_ls).grid(row=1, column=2, padx=3, pady=3)

        tk.Button(frame_ipfs, text="節點資訊 (id)", command=self.ipfs_id).grid(row=2, column=0, padx=3, pady=3)
        tk.Button(frame_ipfs, text="節點版本 (version)", command=self.ipfs_version).grid(row=2, column=1, padx=3, pady=3)
        tk.Button(frame_ipfs, text="網路狀態 (swarm/peers)", command=self.ipfs_swarm_peers).grid(row=2, column=2, padx=3, pady=3)

        tk.Button(frame_ipfs, text="DHT 查詢 (dht/findpeer)", command=self.ipfs_dht_findpeer).grid(row=3, column=0, padx=3, pady=3)
        tk.Button(frame_ipfs, text="PubSub 發佈 (pubsub/pub)", command=self.ipfs_pubsub_pub).grid(row=3, column=1, padx=3, pady=3)
        tk.Button(frame_ipfs, text="PubSub 訂閱 (pubsub/sub)", command=self.ipfs_pubsub_sub).grid(row=3, column=2, padx=3, pady=3)

        tk.Button(frame_ipfs, text="區塊資訊 (block/stat)", command=self.ipfs_block_stat).grid(row=4, column=0, padx=3, pady=3)
        tk.Button(frame_ipfs, text="Repo 狀態 (repo/stat)", command=self.ipfs_repo_stat).grid(row=4, column=1, padx=3, pady=3)
        tk.Button(frame_ipfs, text="設定查詢 (config/show)", command=self.ipfs_config_show).grid(row=4, column=2, padx=3, pady=3)

        # IPFS Cluster 功能按鈕區
        frame_cluster = tk.LabelFrame(self.master, text="IPFS Cluster 功能")
        frame_cluster.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(frame_cluster, text="Pin 新增", command=self.cluster_pin_add).grid(row=0, column=0, padx=3, pady=3)
        tk.Button(frame_cluster, text="Pin 移除", command=self.cluster_pin_rm).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(frame_cluster, text="Pin 列表", command=self.cluster_pin_ls).grid(row=0, column=2, padx=3, pady=3)
        tk.Button(frame_cluster, text="Pin 狀態", command=self.cluster_pin_status).grid(row=0, column=3, padx=3, pady=3)

        tk.Button(frame_cluster, text="集群節點列表", command=self.cluster_peers).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(frame_cluster, text="集群 ID", command=self.cluster_id).grid(row=1, column=1, padx=3, pady=3)
        tk.Button(frame_cluster, text="集群狀態", command=self.cluster_status).grid(row=1, column=2, padx=3, pady=3)
        tk.Button(frame_cluster, text="版本資訊", command=self.cluster_version).grid(row=1, column=3, padx=3, pady=3)

        # 輸出文字區塊
        self.output_text = scrolledtext.ScrolledText(self.master, height=20, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    ### 啟動/停止 ###
    def start_ipfs(self):
        if self.ipfs_proc and self.ipfs_proc.poll() is None:
            self.log("IPFS 已在執行中")
            return

        def run_ipfs():
            self.log("啟動 IPFS daemon...")
            self.ipfs_proc = subprocess.Popen(["ipfs", "daemon"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in self.ipfs_proc.stdout:
                self.log(line.decode(errors='ignore').strip())

        threading.Thread(target=run_ipfs, daemon=True).start()

    def start_cluster(self):
        if self.cluster_proc and self.cluster_proc.poll() is None:
            self.log("IPFS Cluster 已在執行中")
            return

        def run_cluster():
            self.log("啟動 IPFS Cluster 服務...")
            self.cluster_proc = subprocess.Popen(["ipfs-cluster-service", "daemon"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in self.cluster_proc.stdout:
                self.log(line.decode(errors='ignore').strip())

        threading.Thread(target=run_cluster, daemon=True).start()

    def stop_all(self):
        self.log("停止 IPFS 和 Cluster...")
        if self.ipfs_proc and self.ipfs_proc.poll() is None:
            self.ipfs_proc.terminate()
            self.ipfs_proc.wait()
            self.log("IPFS 已停止")
        if self.cluster_proc and self.cluster_proc.poll() is None:
            self.cluster_proc.terminate()
            self.cluster_proc.wait()
            self.log("Cluster 已停止")

    def on_close(self):
        self.stop_all()
        self.master.destroy()

    ### IPFS API 功能 ###

    def ipfs_add(self):
        if not self.check_ipfs_running():
            return
        filepath = filedialog.askopenfilename()
        if not filepath:
            return
        self.log(f"加入檔案到 IPFS: {filepath}")
        try:
            with open(filepath, "rb") as f:
                files = {"file": f}
                r = requests.post(f"{self.ipfs_api_url}/add", files=files)
            result = r.json()
            self.log(json.dumps(result, indent=2))
        except Exception as e:
            self.log(f"加入失敗: {e}")

    def ipfs_cat(self):
        if not self.check_ipfs_running():
            return
        cid = simpledialog.askstring("ipfs cat", "請輸入 CID:")
        if not cid:
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/cat", params={"arg": cid})
            r.raise_for_status()
            self.log(f"內容：\n{r.text[:1000]}...")  # 只顯示前1000字
        except Exception as e:
            self.log(f"取得內容失敗: {e}")

    def ipfs_ls(self):
        if not self.check_ipfs_running():
            return
        cid = simpledialog.askstring("ipfs ls", "請輸入 CID:")
        if not cid:
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/ls", params={"arg": cid})
            r.raise_for_status()
            result = r.json()
            self.log(json.dumps(result, indent=2))
        except Exception as e:
            self.log(f"列出失敗: {e}")

    def ipfs_pin_add(self):
        if not self.check_ipfs_running():
            return
        cid = simpledialog.askstring("pin add", "請輸入要 Pin 的 CID:")
        if not cid:
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/pin/add", params={"arg": cid})
            r.raise_for_status()
            self.log(f"Pin 新增成功: {cid}")
        except Exception as e:
            self.log(f"Pin 新增失敗: {e}")

    def ipfs_pin_rm(self):
        if not self.check_ipfs_running():
            return
        cid = simpledialog.askstring("pin rm", "請輸入要 Unpin 的 CID:")
        if not cid:
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/pin/rm", params={"arg": cid})
            r.raise_for_status()
            self.log(f"Pin 移除成功: {cid}")
        except Exception as e:
            self.log(f"Pin 移除失敗: {e}")

    def ipfs_pin_ls(self):
        if not self.check_ipfs_running():
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/pin/ls")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Pin 列表失敗: {e}")

    def ipfs_id(self):
        if not self.check_ipfs_running():
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/id")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"取得節點ID失敗: {e}")

    def ipfs_version(self):
        if not self.check_ipfs_running():
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/version")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"取得版本失敗: {e}")

    def ipfs_swarm_peers(self):
        if not self.check_ipfs_running():
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/swarm/peers")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"取得 peers 失敗: {e}")

    def ipfs_dht_findpeer(self):
        if not self.check_ipfs_running():
            return
        peer_id = simpledialog.askstring("dht findpeer", "請輸入 Peer ID:")
        if not peer_id:
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/dht/findpeer", params={"arg": peer_id})
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"DHT 查詢失敗: {e}")

    def ipfs_pubsub_pub(self):
        if not self.check_ipfs_running():
            return
        topic = simpledialog.askstring("PubSub 發佈", "請輸入主題 (topic):")
        message = simpledialog.askstring("PubSub 發佈", "請輸入訊息內容:")
        if not topic or not message:
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/pubsub/pub", params={"arg": topic, "arg": message})
            r.raise_for_status()
            self.log(f"已發佈到 {topic}")
        except Exception as e:
            self.log(f"發佈失敗: {e}")

    def ipfs_pubsub_sub(self):
        if not self.check_ipfs_running():
            return
        topic = simpledialog.askstring("PubSub 訂閱", "請輸入主題 (topic):")
        if not topic:
            return

        # 以非同步監聽來實作較複雜，這裡簡單示範API呼叫列出訂閱主題
        try:
            r = requests.post(f"{self.ipfs_api_url}/pubsub/ls")
            r.raise_for_status()
            self.log(f"目前訂閱主題:\n{r.text}")
        except Exception as e:
            self.log(f"訂閱失敗: {e}")

    def ipfs_block_stat(self):
        if not self.check_ipfs_running():
            return
        cid = simpledialog.askstring("block stat", "請輸入 CID:")
        if not cid:
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/block/stat", params={"arg": cid})
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Block stat 失敗: {e}")

    def ipfs_repo_stat(self):
        if not self.check_ipfs_running():
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/repo/stat")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Repo stat 失敗: {e}")

    def ipfs_config_show(self):
        if not self.check_ipfs_running():
            return
        try:
            r = requests.post(f"{self.ipfs_api_url}/config/show")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Config show 失敗: {e}")

    ### IPFS Cluster API 功能 ###

    def cluster_pin_add(self):
        if not self.check_cluster_running():
            return
        cid = simpledialog.askstring("Cluster Pin 新增", "請輸入 CID:")
        if not cid:
            return
        try:
            r = requests.post(f"{self.cluster_api_url}/pins/{cid}")
            if r.status_code == 202:
                self.log(f"Pin 新增請求已送出: {cid}")
            else:
                self.log(f"Pin 新增失敗: {r.status_code} {r.text}")
        except Exception as e:
            self.log(f"Cluster Pin 新增失敗: {e}")

    def cluster_pin_rm(self):
        if not self.check_cluster_running():
            return
        cid = simpledialog.askstring("Cluster Pin 移除", "請輸入 CID:")
        if not cid:
            return
        try:
            r = requests.delete(f"{self.cluster_api_url}/pins/{cid}")
            if r.status_code == 202:
                self.log(f"Pin 移除請求已送出: {cid}")
            else:
                self.log(f"Pin 移除失敗: {r.status_code} {r.text}")
        except Exception as e:
            self.log(f"Cluster Pin 移除失敗: {e}")

    def cluster_pin_ls(self):
        if not self.check_cluster_running():
            return
        try:
            r = requests.get(f"{self.cluster_api_url}/pins")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Cluster Pin 列表失敗: {e}")

    def cluster_pin_status(self):
        if not self.check_cluster_running():
            return
        cid = simpledialog.askstring("Cluster Pin 狀態", "請輸入 CID:")
        if not cid:
            return
        try:
            r = requests.get(f"{self.cluster_api_url}/pins/{cid}")
            if r.status_code == 200:
                self.log(json.dumps(r.json(), indent=2))
            else:
                self.log(f"Pin 狀態查詢失敗: {r.status_code} {r.text}")
        except Exception as e:
            self.log(f"Cluster Pin 狀態查詢失敗: {e}")

    def cluster_peers(self):
        if not self.check_cluster_running():
            return
        try:
            r = requests.get(f"{self.cluster_api_url}/peers")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Cluster Peers 取得失敗: {e}")

    def cluster_id(self):
        if not self.check_cluster_running():
            return
        try:
            r = requests.get(f"{self.cluster_api_url}/id")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Cluster ID 取得失敗: {e}")

    def cluster_status(self):
        if not self.check_cluster_running():
            return
        try:
            r = requests.get(f"{self.cluster_api_url}/health")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Cluster 狀態取得失敗: {e}")

    def cluster_version(self):
        if not self.check_cluster_running():
            return
        try:
            r = requests.get(f"{self.cluster_api_url}/version")
            r.raise_for_status()
            self.log(json.dumps(r.json(), indent=2))
        except Exception as e:
            self.log(f"Cluster 版本取得失敗: {e}")

    ### 檢查服務是否執行 ###
    def check_ipfs_running(self):
        if not self.ipfs_proc or self.ipfs_proc.poll() is not None:
            messagebox.showerror("錯誤", "IPFS 未啟動")
            return False
        return True

    def check_cluster_running(self):
        if not self.cluster_proc or self.cluster_proc.poll() is not None:
            messagebox.showerror("錯誤", "IPFS Cluster 未啟動")
            return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = IPFSClusterFullApp(root)
    root.mainloop()
