//
//  AppDelegate.swift
//  msg
//
//  Created by Harry Maclean on 29/11/2014.
//  Copyright (c) 2014 Harry Maclean. All rights reserved.
//

import Cocoa

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate, NSOutlineViewDataSource, NSOutlineViewDelegate {

    @IBOutlet weak var window: NSWindow!
    @IBOutlet weak var conversationView: NSTextField!
    @IBOutlet weak var conversationPicker: NSOutlineView!
    @IBOutlet weak var messageField: NSTextField!
    
    var username: String = "alice"
    let wd: String = NSBundle.mainBundle().pathForResource("client", ofType: "")!
    
    var recipients: [String] = []


    func applicationDidFinishLaunching(aNotification: NSNotification) {
        let fm = NSFileManager.defaultManager()
        
        // Setup virtualenv
        if !fm.fileExistsAtPath("\(wd)/env") {
            setup_virutalenv()
        }
        
        if let u: String = NSBundle.mainBundle().infoDictionary?["username"] as? String {
            username = u
        }
        
        if let cs = conversations()? {
            recipients = cs
            if let conv = conversation(cs[0]) {
                render_conversation(conv)
            }
        }
        
        conversationPicker.setDataSource(self)
        conversationPicker.setDelegate(self)

    }

    func applicationWillTerminate(aNotification: NSNotification) {
        // Insert code here to tear down your application
    }
    
    func render_conversation(conv: [[String]]) {
        var conv_text = ""
        for c in conv {
            conv_text += c[0] + ": " + c[2] + "\n"
        }
        conversationView.stringValue = conv_text
    }
    
    func conversations() -> [String]? {
        if let res = exec("\(wd)/cli", args: ["list-conversations", username])?.dataUsingEncoding(NSUTF8StringEncoding, allowLossyConversion: false) {
            var err: NSError?
            return NSJSONSerialization.JSONObjectWithData(res, options: NSJSONReadingOptions.AllowFragments, error: &err) as [String]?
        }
        return nil
    }
    
    func conversation(name: String) -> [[String]]? {
        if let res = exec("\(wd)/cli", args: ["show-conversation", username, "--recipient", name])?.dataUsingEncoding(NSUTF8StringEncoding, allowLossyConversion: false) {
            var err: NSError?
            return NSJSONSerialization.JSONObjectWithData(res, options: NSJSONReadingOptions.AllowFragments, error: &err) as [[String]]?
        }
        return nil
    }
    
    func send_message(recipient: String, msg: String) {
        exec("\(wd)/cli", args: ["send-message", username, "--recipient", recipient, "--body", msg])
    }
    
    func exec(path: NSString, args: [NSString]) -> String? {
        let cli_path = NSBundle.mainBundle().pathForResource("client", ofType: "")!
        var task = NSTask()
        task.launchPath = path
        task.arguments = args
        var pipe = NSPipe()
        task.standardOutput = pipe
        task.currentDirectoryPath = cli_path
        task.launch()
        let handle = pipe.fileHandleForReading
        let data = handle.readDataToEndOfFile()
        if let string = NSString(data: data, encoding: NSUTF8StringEncoding) {
            return Optional.Some(string)
        }
        return Optional.None
    }
    
    func setup_virutalenv() {
        let cli_path = NSBundle.mainBundle().pathForResource("client", ofType: "")!
        println("creating a virtualenv")
        exec("/usr/local/bin/virtualenv", args:["env"])
        println("installing dependencies")
        exec("./env/bin/pip", args:["install", "-r", "requirements.txt"])
    }
    
    @IBAction func sendMessage(sender: NSTextField) {
        if conversationPicker.selectedRow == -1 {
            return
        }
        let recipient = recipients[conversationPicker.selectedRow]
        send_message(recipient, msg: sender.stringValue)
        sender.stringValue = ""
        if let conv = conversation(recipient) {
            render_conversation(conv)
        }
    }
    
    
    // NSOutlineViewDataSource Protocol
    
    func outlineView(outlineView: NSOutlineView, child index: Int, ofItem item: AnyObject?) -> AnyObject {
        // We have a flat structure, so we assume item is nil and just return recipients[index]
        return recipients[index]
    }
    
    func outlineView(outlineView: NSOutlineView, isItemExpandable item: AnyObject) -> Bool {
        return false
    }
    
    func outlineView(outlineView: NSOutlineView, numberOfChildrenOfItem item: AnyObject?) -> Int {
        // Again, just we assume item is nil and return recipients.count
        return recipients.count
    }
    
    func outlineView(outlineView: NSOutlineView, objectValueForTableColumn tableColumn: NSTableColumn?, byItem item: AnyObject?) -> AnyObject? {
        // No idea what we should return here tbh..
        return item
    }
    
    // NSOutlineViewDelegate Protocol
    
    func outlineViewSelectionDidChange(notification: NSNotification) {
        let recipient = recipients[conversationPicker.selectedRow]
        if let conv = conversation(recipient) {
            render_conversation(conv)
        }
        messageField.stringValue = ""
    }

}

