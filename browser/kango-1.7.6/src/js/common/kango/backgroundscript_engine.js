var core=require("kango/core"),extensionInfo=require("kango/extension_info"),lang=require("kango/lang"),io=require("kango/io"),console=require("kango/console"),utils=require("kango/utils"),func=utils.func,object=utils.object,EventTarget=utils.EventTarget;function BackgroundScriptEngine(){this._window=this._sandbox=null;EventTarget.call(this)}
BackgroundScriptEngine.prototype=object.extend(EventTarget,{init:function(){var b=core.createApiInstance("background");this._sandbox=lang.createHTMLSandbox("background.html",func.bind(function(a){this._window=a;this.fireEvent("init",{window:a});this._initScripts(a,b.obj,func.bind(function(){this.fireEvent("load",{window:a})},this))},this),func.bind(function(a){b.clear();this.fireEvent("unload",{window:a})},this))},getDOMWindow:function(){return this._window},dispose:function(){this.removeAllEventListeners();
this._window=null;null!=this._sandbox&&(this._sandbox.dispose(),this._sandbox=null)},isLoaded:function(){var b=this.getDOMWindow();return null!=b&&"complete"==b.document.readyState&&"undefined"!=typeof b.kango},_initScripts:function(b,a,g){object.forEach(a,function(h,a){b[a]=h});var e=b.document,c=extensionInfo.background_scripts;if("undefined"!=typeof c&&0<c.length){var d=0,f=function(){var a=e.createElement("script");a.setAttribute("type","text/javascript");a.setAttribute("src",io.getExtensionFileUrl(c[d]));
var b=function(){d++;d<c.length?f():g()};a.onerror=function(){console.error("Unable to load "+c[d])};"undefined"!=typeof a.onreadystatechange?a.onreadystatechange=function(){"complete"==a.readyState&&b()}:a.onload=b;e.body.appendChild(a)};f()}}});module.exports=new BackgroundScriptEngine;core.addEventListener("ready",function(){module.exports.init()});