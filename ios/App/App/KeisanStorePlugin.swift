import Foundation
import Capacitor
import StoreKit

// App Store の こうにゅう（StoreKit 2）と はなす ぶひん。そと の サーバー や かきん サービス は つかわない。
// JavaScript からは Capacitor.Plugins.KeisanStore で よぶ。
// - 30にち の おためし：0えん の ひしょうもうがた（trial30）。かった ひ から 30にち（ひにち の けいさん は index.html）
// - つきがく：じどう こうしん の サブスクリプション（monthly）
@objc(KeisanStorePlugin)
public class KeisanStorePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "KeisanStorePlugin"
    public let jsName = "KeisanStore"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "getStatus", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "getProducts", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "purchase", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "restore", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "manage", returnType: CAPPluginReturnPromise)
    ]

    static let trialID = "jp.katsuya.keisanrenshu.trial30"
    static let monthlyID = "jp.katsuya.keisanrenshu.monthly"

    private var updates: Task<Void, Never>?

    override public func load() {
        // ほか の たんまつ（ファミリー きょうゆう など）や こうしん・かいやく で かわった とき に しらせる
        updates = Task { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let transaction) = result { await transaction.finish() }
                self?.notifyListeners("change", data: [:])
            }
        }
    }

    deinit { updates?.cancel() }

    // いま つかえる もの：おためし を はじめた とき（ミリびょう）と、つきがく に とうろく ちゅう か
    private func currentStatus() async -> [String: Any] {
        var status: [String: Any] = ["subscribed": false]
        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result, transaction.revocationDate == nil else { continue }
            switch transaction.productID {
            case Self.trialID:
                status["trialStart"] = transaction.originalPurchaseDate.timeIntervalSince1970 * 1000
            case Self.monthlyID:
                if let expires = transaction.expirationDate {
                    if expires < Date() { continue }
                    status["expires"] = expires.timeIntervalSince1970 * 1000
                }
                status["subscribed"] = true
            default:
                break
            }
        }
        return status
    }

    @objc func getStatus(_ call: CAPPluginCall) {
        Task {
            let status = await currentStatus()
            call.resolve(status)
        }
    }

    // ねだん の ひょうじ（App Store に とうろく した もの）
    @objc func getProducts(_ call: CAPPluginCall) {
        Task {
            do {
                let products = try await Product.products(for: [Self.trialID, Self.monthlyID])
                let list = products.map { ["id": $0.id, "displayPrice": $0.displayPrice, "displayName": $0.displayName] }
                call.resolve(["products": list])
            } catch {
                call.reject(error.localizedDescription, "failed")
            }
        }
    }

    // result：success（できた）・cancelled（やめた）・pending（ほごしゃ の しょうにん まち など）
    @objc func purchase(_ call: CAPPluginCall) {
        guard let id = call.getString("productId"), id == Self.trialID || id == Self.monthlyID else {
            call.reject("productId が ありません", "badRequest")
            return
        }
        Task { @MainActor in
            do {
                guard let product = try await Product.products(for: [id]).first else {
                    call.reject("しょうひん が みつかりません", "notFound")
                    return
                }
                switch try await product.purchase() {
                case .success(let verification):
                    guard case .verified(let transaction) = verification else {
                        call.resolve(["result": "unverified"])
                        return
                    }
                    await transaction.finish()
                    var data = await self.currentStatus()
                    data["result"] = "success"
                    call.resolve(data)
                case .userCancelled:
                    call.resolve(["result": "cancelled"])
                case .pending:
                    call.resolve(["result": "pending"])
                @unknown default:
                    call.resolve(["result": "unknown"])
                }
            } catch {
                call.reject(error.localizedDescription, "failed")
            }
        }
    }

    // こうにゅう を ふくげん する（App Store と どうき して から、いま の じょうたい を かえす）
    @objc func restore(_ call: CAPPluginCall) {
        Task {
            do {
                try await AppStore.sync()
                let status = await currentStatus()
                call.resolve(status)
            } catch {
                call.reject(error.localizedDescription, "failed")
            }
        }
    }

    // とうろく の かくにん・かいやく（App Store の がめん を ひらく）
    @objc func manage(_ call: CAPPluginCall) {
        Task { @MainActor in
            guard let scene = self.bridge?.viewController?.view.window?.windowScene else {
                call.reject("がめん が みつかりません", "failed")
                return
            }
            do {
                try await AppStore.showManageSubscriptions(in: scene)
                call.resolve()
            } catch {
                call.reject(error.localizedDescription, "failed")
            }
        }
    }
}

// アプリ の なか の ぶひん（KeisanStorePlugin）を つかえる ように する
class MainViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        bridge?.registerPluginInstance(KeisanStorePlugin())
    }
}
