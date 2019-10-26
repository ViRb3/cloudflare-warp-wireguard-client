// frida -U -l frida-cloudflare.js -f com.cloudflare.onedotonedotonedotone --no-pause

/* 
BYPASS OKHTTP3 SSL PINNING

Magic strings:
"Certificate pinning failure!"
"\n  Peer certificate chain:"
"\n  Pinned certificates for "
public void a(String arg1, List arg2) throws SSLPeerUnverifiedException
".*"
*/

Java.perform(function () {
    var target = Java.use('...');
    target.a.overload('java.lang.String', 'java.util.List')
        .implementation = function (arg1, arg2) {
            return;
        };
});

/*
DUMP DECRYPTED STRINGS

Magic strings:
"getDecryptionCipher(iv).doFinal(encryptedData)"
"Caught exception in decryptString(): "
*/

Java.perform(function () {
    var target = Java.use('...');
    target.a.overload('java.lang.String')
        .implementation = function (arg1) {
            var result = this.a(arg1);
            console.log("Arg: " + arg1);
            console.log("Result: " + result);
            return result;
        };
});
