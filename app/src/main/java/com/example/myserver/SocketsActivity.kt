package com.example.myserver

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.widget.Button
import android.widget.ScrollView
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import org.zeromq.SocketType
import org.zeromq.ZContext
import org.zeromq.ZMQ
import kotlin.concurrent.thread

class SocketsActivity : AppCompatActivity() {
    private lateinit var tvStatus: TextView
    private lateinit var tvMessages: TextView
    private lateinit var btnStartClient: Button
    private lateinit var btnSendMessage: Button
    private lateinit var btnClearLog: Button
    private lateinit var btnBack: Button
    private lateinit var scrollView: ScrollView

    private lateinit var handler: Handler
    private var isClientRunning = false
    private var clientThread: Thread? = null

    companion object {
        private const val TAG = "SocketsActivity"
        //private const val SERVER_IP = "192.168.0.101" //реальный
        private const val SERVER_IP = "10.0.2.2" // эмулятор
        private const val SERVER_PORT = 5555
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_sockets)

        enableEdgeToEdge()
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        tvStatus = findViewById(R.id.tvStatus)
        tvMessages = findViewById(R.id.tvMessages)
        btnStartClient = findViewById(R.id.btnStartClient)
        btnSendMessage = findViewById(R.id.btnSendMessage)
        btnClearLog = findViewById(R.id.btnClearLog)
        btnBack = findViewById(R.id.btnBack)
        scrollView = findViewById(R.id.scrollView)

        handler = Handler(Looper.getMainLooper())
        setupUI()
    }

    private fun setupUI() {
        btnStartClient.setOnClickListener {
            if (!isClientRunning) {
                startClient()
                btnStartClient.text = "Stop Client"
                btnStartClient.isEnabled = false
                tvStatus.text = "Connecting to server..."
            } else {
                stopClient()
                btnStartClient.text = "Start Client"
                tvStatus.text = "Client stopped"
                btnSendMessage.isEnabled = false
            }
            isClientRunning = !isClientRunning
        }

        btnSendMessage.setOnClickListener {
            if (isClientRunning) {
                sendMessageToServer()
            } else {
                tvStatus.text = "Start client first!"
            }
        }

        btnClearLog.setOnClickListener {
            tvMessages.text = ""
        }

        btnBack.setOnClickListener {
            stopClient()
            finish()
        }

        btnSendMessage.isEnabled = false
    }

    private fun startClient() {
        clientThread = thread {
            try {
                ZContext().use { context ->
                    context.createSocket(SocketType.REQ).use { socket ->
                        val serverAddress = "tcp://$SERVER_IP:$SERVER_PORT"
                        Log.d(TAG, "Connecting to: $serverAddress")

                        socket.connect(serverAddress)
                        socket.setSendTimeOut(5000)
                        socket.setReceiveTimeOut(5000)

                        val testMessage = "Hello from Android!"
                        socket.send(testMessage.toByteArray(ZMQ.CHARSET), 0)

                        val reply = socket.recv(0)
                        val replyString = String(reply, ZMQ.CHARSET)

                        handler.post {
                            tvMessages.append("Connected!\n")
                            tvMessages.append("Server: $replyString\n\n")
                            tvStatus.text = "Connected to $SERVER_IP"
                            btnStartClient.isEnabled = true
                            btnStartClient.text = "Stop Client"
                            btnSendMessage.isEnabled = true
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error: ${e.message}")
                handler.post {
                    tvStatus.text = "Failed: ${e.message}"
                    tvMessages.append("Error: ${e.message}\n")
                    btnStartClient.isEnabled = true
                    btnStartClient.text = "Start Client"
                    btnSendMessage.isEnabled = false
                    isClientRunning = false
                }
            }
        }
    }

    private fun sendMessageToServer() {
        thread {
            try {
                ZContext().use { context ->
                    context.createSocket(SocketType.REQ).use { socket ->
                        val serverAddress = "tcp://$SERVER_IP:$SERVER_PORT"
                        socket.connect(serverAddress)
                        socket.setSendTimeOut(3000)
                        socket.setReceiveTimeOut(3000)

                        val message = "Hello from Android! ${System.currentTimeMillis()}"
                        socket.send(message.toByteArray(ZMQ.CHARSET), 0)

                        val reply = socket.recv(0)
                        val replyString = String(reply, ZMQ.CHARSET)

                        handler.post {
                            tvMessages.append("Sent: $message\n")
                            tvMessages.append("Got: $replyString\n\n")
                            scrollView.post {
                                scrollView.fullScroll(android.view.View.FOCUS_DOWN)
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Send error: ${e.message}")
                handler.post {
                    tvStatus.text = "Send failed: ${e.message}"
                    tvMessages.append("Send error: ${e.message}\n")
                }
            }
        }
    }

    private fun stopClient() {
        clientThread?.interrupt()
        clientThread = null
    }

    override fun onDestroy() {
        super.onDestroy()
        stopClient()
    }
}