import java.net.*;
import java.util.*;

public class MacTest {
    public static void main(String[] args) throws Exception {
        // Method 1: InetAddress.getLocalHost() - old way (clientEthName=null)
        InetAddress localHost = InetAddress.getLocalHost();
        System.out.println("=== getLocalHost method (OLD) ===");
        System.out.println("hostname: " + localHost.getHostName());
        System.out.println("IP: " + localHost.getHostAddress());
        NetworkInterface niByAddr = NetworkInterface.getByInetAddress(localHost);
        if (niByAddr != null) {
            System.out.println("NI name: " + niByAddr.getName());
            byte[] mac = niByAddr.getHardwareAddress();
            if (mac != null) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < mac.length; i++) {
                    sb.append(String.format("%02x", mac[i]));
                    if (i < mac.length - 1) sb.append(":");
                }
                System.out.println("MAC: " + sb.toString());
            } else {
                System.out.println("MAC: null (no hardware address!)");
            }
        } else {
            System.out.println("NI: null (no interface found!)");
        }

        System.out.println();

        // Method 2: getByName("enp2s0") - new way (clientEthName=enp2s0)
        System.out.println("=== getByName(enp2s0) method (NEW) ===");
        NetworkInterface niByName = NetworkInterface.getByName("enp2s0");
        if (niByName != null) {
            System.out.println("NI name: " + niByName.getName());
            byte[] mac = niByName.getHardwareAddress();
            if (mac != null) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < mac.length; i++) {
                    sb.append(String.format("%02x", mac[i]));
                    if (i < mac.length - 1) sb.append(":");
                }
                System.out.println("MAC: " + sb.toString());
            } else {
                System.out.println("MAC: null");
            }
        } else {
            System.out.println("NI: null (enp4s0 not found!)");
        }

        System.out.println();

        // Method 3: List all interfaces
        System.out.println("=== All network interfaces ===");
        Enumeration<NetworkInterface> nis = NetworkInterface.getNetworkInterfaces();
        while (nis.hasMoreElements()) {
            NetworkInterface ni = nis.nextElement();
            byte[] mac = ni.getHardwareAddress();
            String macStr = "null";
            if (mac != null) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < mac.length; i++) {
                    sb.append(String.format("%02x", mac[i]));
                    if (i < mac.length - 1) sb.append(":");
                }
                macStr = sb.toString();
            }
            System.out.println(ni.getName() + " -> MAC: " + macStr + " (up=" + ni.isUp() + ", loopback=" + ni.isLoopback() + ")");
        }
    }
}
